import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session
from flask_migrate import Migrate
from models import db, User, ChatSession, ChatMessage, DailyUsage, Disease, SubscriptionPlan
from model import SymptomMatcher
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "medical_chatbot_secret_key_2024")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Global variables
symptom_matcher = None

def load_initial_data():
    """Load initial subscription plans and diseases from JSON files"""
    try:
        # Load plans data
        with open('plans.json', 'r') as f:
            plans_data = json.load(f)
        
        # Add subscription plans to database
        for plan_key, plan_info in plans_data.items():
            existing_plan = SubscriptionPlan.query.filter_by(plan_key=plan_key).first()
            if not existing_plan:
                plan = SubscriptionPlan(
                    plan_key=plan_key,
                    name=plan_info['name'],
                    price=plan_info['price'],
                    max_chats_per_day=plan_info['max_chats_per_day'],
                    max_bot_responses_per_chat=plan_info['max_bot_responses_per_chat'],
                    medicine_images=plan_info['medicine_images'],
                    chat_history=plan_info['chat_history'],
                    voice_chat=plan_info['voice_chat'],
                    available_languages=plan_info['available_languages'],
                    layout=plan_info['layout'],
                    features=plan_info['features']
                )
                db.session.add(plan)
            else:
                # Update existing plan with new fields
                existing_plan.max_bot_responses_per_chat = plan_info['max_bot_responses_per_chat']
                existing_plan.layout = plan_info['layout']
                existing_plan.voice_chat = plan_info['voice_chat']
                existing_plan.available_languages = plan_info['available_languages']
                existing_plan.features = plan_info['features']
        
        # Load diseases data
        with open('diseases_data.json', 'r') as f:
            diseases_data = json.load(f)
        
        # Add diseases to database
        for disease_info in diseases_data:
            existing_disease = Disease.query.filter_by(name=disease_info['disease']).first()
            if not existing_disease:
                disease = Disease(
                    name=disease_info['disease'],
                    symptoms=disease_info['symptoms'],
                    medicines=disease_info['medicines']
                )
                db.session.add(disease)
        
        db.session.commit()
        logging.info("Initial data loaded successfully")
        
    except Exception as e:
        logging.error(f"Error loading initial data: {str(e)}")
        db.session.rollback()

def get_diseases_data():
    """Get diseases data from database"""
    diseases = Disease.query.all()
    return [
        {
            'disease': disease.name,
            'symptoms': disease.symptoms,
            'medicines': disease.medicines
        }
        for disease in diseases
    ]

def init_symptom_matcher():
    """Initialize symptom matcher with database data"""
    global symptom_matcher
    diseases_data = get_diseases_data()
    symptom_matcher = SymptomMatcher(diseases_data)

def get_plans_data():
    """Get subscription plans data from database"""
    plans = SubscriptionPlan.query.all()
    plans_dict = {}
    for plan in plans:
        plans_dict[plan.plan_key] = {
            'name': plan.name,
            'max_chats_per_day': plan.max_chats_per_day,
            'medicine_images': plan.medicine_images,
            'chat_history': plan.chat_history,
            'available_languages': plan.available_languages,
            'price': plan.price,
            'features': plan.features
        }
    return plans_dict

def load_languages():
    """Load language translations from JSON file"""
    try:
        with open('languages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("languages.json file not found")
        return {"languages": {"en": {"name": "English", "flag": "🇺🇸"}}}
    except json.JSONDecodeError:
        logging.error("Invalid JSON in languages.json")
        return {"languages": {"en": {"name": "English", "flag": "🇺🇸"}}}

def get_user_language():
    """Get user language from database"""
    user_id = get_user_id()
    user = get_or_create_user(user_id)
    return user.language if hasattr(user, 'language') else 'en'

def get_available_languages(user_plan):
    """Get available languages based on user plan"""
    if isinstance(user_plan, str):
        plan_data = SubscriptionPlan.query.filter_by(plan_key=user_plan).first()
    else:
        plan_data = user_plan
    
    if plan_data and plan_data.available_languages:
        return plan_data.available_languages
    return ['en', 'hi']  # Default for basic plan

def get_localized_text(key, language='en', **kwargs):
    """Get localized text for given key and language"""
    languages_data = load_languages()
    lang_data = languages_data.get('languages', {}).get(language, {})
    
    if key not in lang_data:
        # Fallback to English
        lang_data = languages_data.get('languages', {}).get('en', {})
    
    text = lang_data.get(key, key)
    
    # Format text with provided kwargs
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass  # Return unformatted text if formatting fails
    
    return text

def get_or_create_user(user_id):
    """Get or create user in database"""
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id, plan='basic')
        db.session.add(user)
        db.session.commit()
    return user

def get_user_id():
    """Get or create user ID from session"""
    if 'user_id' not in session:
        session['user_id'] = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return session['user_id']

def get_user_plan():
    """Get user plan string from database"""
    user_id = get_user_id()
    user = get_or_create_user(user_id)
    return user.plan

def get_user_plan_object():
    """Get user plan object from database"""
    user_id = get_user_id()
    user = get_or_create_user(user_id)
    return SubscriptionPlan.query.filter_by(plan_key=user.plan).first()

def check_daily_limit(user_id, plan):
    """Check if user has exceeded daily chat limit"""
    today = datetime.now().strftime('%Y-%m-%d')
    user = get_or_create_user(user_id)
    
    # Get or create daily usage record
    usage = DailyUsage.query.filter_by(user_id=user.id, date=today).first()
    if not usage:
        usage = DailyUsage(user_id=user.id, date=today, chat_count=0)
        db.session.add(usage)
        db.session.commit()
    
    plan_key = plan if isinstance(plan, str) else plan.plan_key
    plan_data = SubscriptionPlan.query.filter_by(plan_key=plan_key).first()
    max_chats = plan_data.max_chats_per_day if plan_data else 2
    
    return usage.chat_count < max_chats

def increment_daily_usage(user_id):
    """Increment daily usage counter"""
    today = datetime.now().strftime('%Y-%m-%d')
    user = get_or_create_user(user_id)
    
    usage = DailyUsage.query.filter_by(user_id=user.id, date=today).first()
    if not usage:
        usage = DailyUsage(user_id=user.id, date=today, chat_count=1)
        db.session.add(usage)
    else:
        usage.chat_count += 1
    
    db.session.commit()

def check_bot_response_limit(chat_session, plan):
    """Check if bot has reached response limit for current chat"""
    plan_key = plan if isinstance(plan, str) else plan.plan_key
    plan_data = SubscriptionPlan.query.filter_by(plan_key=plan_key).first()
    if not plan_data or plan_data.max_bot_responses_per_chat == 999:  # Unlimited
        return False
    
    return chat_session.bot_response_count >= plan_data.max_bot_responses_per_chat

def increment_bot_response_count(chat_session):
    """Increment bot response counter for current chat"""
    chat_session.bot_response_count += 1
    db.session.commit()

@app.route('/')
def index():
    """Main chat interface"""
    user_id = get_user_id()
    user_plan = get_user_plan()
    user_language = get_user_language()
    plans_data = get_plans_data()
    languages_data = load_languages()
    available_languages = get_available_languages(user_plan)
    
    return render_template('index.html', 
                         user_plan=user_plan, 
                         user_language=user_language,
                         plans=plans_data,
                         languages=languages_data['languages'],
                         available_languages=available_languages,
                         user_id=user_id)

@app.route('/switch_plan', methods=['POST'])
def switch_plan():
    """Switch user subscription plan"""
    new_plan = request.json.get('plan', 'basic')
    plan_exists = SubscriptionPlan.query.filter_by(plan_key=new_plan).first()
    
    if plan_exists:
        user_id = get_user_id()
        user = get_or_create_user(user_id)
        user.plan = new_plan
        db.session.commit()
        return jsonify({'status': 'success', 'new_plan': new_plan})
    return jsonify({'status': 'error', 'message': 'Invalid plan'}), 400

@app.route('/switch_language', methods=['POST'])
def switch_language():
    """Switch user language"""
    new_language = request.json.get('language', 'en')
    user_id = get_user_id()
    user_plan = get_user_plan()
    
    # Check if language is available in current plan
    available_languages = get_available_languages(user_plan)
    
    if new_language in available_languages:
        user = get_or_create_user(user_id)
        user.language = new_language
        db.session.commit()
        
        language_name = load_languages()['languages'].get(new_language, {}).get('name', new_language)
        return jsonify({
            'status': 'success', 
            'new_language': new_language,
            'language_name': language_name
        })
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Language not available in your current plan'
        }), 400

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        user_id = get_user_id()
        user_plan = get_user_plan()
        message = request.json.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Check daily limit
        if not check_daily_limit(user_id, user_plan):
            plan_data = SubscriptionPlan.query.filter_by(plan_key=user_plan).first()
            max_chats = plan_data.max_chats_per_day if plan_data else 2
            return jsonify({
                'error': f'Daily chat limit reached ({max_chats} chats). Please upgrade your plan or try again tomorrow.'
            }), 429
        
        # Initialize symptom matcher if needed
        if symptom_matcher is None:
            init_symptom_matcher()
        
        # Get or create user and session
        user = get_or_create_user(user_id)
        chat_session = ChatSession.query.filter_by(user_id=user.id).order_by(ChatSession.updated_at.desc()).first()
        
        if not chat_session:
            chat_session = ChatSession(
                user_id=user.id,
                session_data={'messages': [], 'current_symptoms': [], 'awaiting_symptoms': False},
                bot_response_count=0
            )
            db.session.add(chat_session)
            db.session.commit()
            # Increment daily usage for new chat
            increment_daily_usage(user_id)
        
        # Check bot response limit for current chat session
        if check_bot_response_limit(chat_session, user_plan):
            plan_data = SubscriptionPlan.query.filter_by(plan_key=user_plan).first()
            max_responses = plan_data.max_bot_responses_per_chat if plan_data else 2
            return jsonify({
                'message': f'Bot response limit reached for this chat ({max_responses} responses). Please start a new chat session.',
                'limit_reached': True
            }), 200
        
        # Process the message
        response = process_user_message(message, chat_session, user_plan)
        
        # Save user message
        user_message = ChatMessage(
            session_id=chat_session.id,
            message_type='user',
            content=message
        )
        db.session.add(user_message)
        
        # Save bot response
        bot_message = ChatMessage(
            session_id=chat_session.id,
            message_type='bot',
            content=response.get('message', ''),
            disease=response.get('disease'),
            medicines=response.get('medicines', [])
        )
        db.session.add(bot_message)
        
        # Increment bot response counter
        increment_bot_response_count(chat_session)
        
        # Update session data
        session_data = chat_session.session_data
        session_data['messages'].append({
            'type': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        session_data['messages'].append({
            'type': 'bot',
            'content': response.get('message', ''),
            'medicines': response.get('medicines', []),
            'disease': response.get('disease', ''),
            'timestamp': datetime.now().isoformat()
        })
        chat_session.session_data = session_data
        chat_session.updated_at = datetime.now()
        
        # Increment usage counter
        increment_daily_usage(user_id)
        
        db.session.commit()
        
        # Add bot response limit info to response
        plan_data = SubscriptionPlan.query.filter_by(plan_key=user_plan).first()
        response['bot_responses_left'] = max(0, plan_data.max_bot_responses_per_chat - chat_session.bot_response_count) if plan_data and plan_data.max_bot_responses_per_chat != 999 else -1
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred while processing your message. Please try again.'}), 500

@app.route('/new_chat', methods=['POST'])
def new_chat():
    """Start a new chat session"""
    try:
        user_id = get_user_id()
        user_plan = get_user_plan()
        
        # Check daily limit
        if not check_daily_limit(user_id, user_plan):
            plan_data = SubscriptionPlan.query.filter_by(plan_key=user_plan).first()
            max_chats = plan_data.max_chats_per_day if plan_data else 2
            return jsonify({
                'error': f'Daily chat limit reached ({max_chats} chats). Please upgrade your plan or try again tomorrow.'
            }), 429
        
        # Create new chat session
        user = get_or_create_user(user_id)
        chat_session = ChatSession(
            user_id=user.id,
            session_data={'messages': [], 'current_symptoms': [], 'awaiting_symptoms': False},
            bot_response_count=0
        )
        db.session.add(chat_session)
        db.session.commit()
        
        # Increment daily usage
        increment_daily_usage(user_id)
        
        return jsonify({
            'message': 'New chat session started! How can I help you today?',
            'session_id': chat_session.id
        })
        
    except Exception as e:
        logging.error(f"Error starting new chat: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to start new chat. Please try again.'}), 500

def process_user_message(message, chat_session, user_plan):
    """Process user message and generate appropriate response"""
    message_lower = message.lower()
    session_data = chat_session.session_data
    user_language = get_user_language()
    
    # Extract symptoms from message
    potential_symptoms = symptom_matcher.extract_symptoms(message_lower)
    
    if potential_symptoms:
        # Add new symptoms to current list
        for symptom in potential_symptoms:
            if symptom not in session_data['current_symptoms']:
                session_data['current_symptoms'].append(symptom)
        
        session_data['awaiting_symptoms'] = True
        
        # If we have enough symptoms, try to match a disease
        if len(session_data['current_symptoms']) >= 2:
            # Try to find matching disease
            disease_match = symptom_matcher.match_disease(session_data['current_symptoms'])
            
            if disease_match:
                medicines = disease_match.get('medicines', [])
                
                # Build medicine information based on plan
                plan_data = SubscriptionPlan.query.filter_by(plan_key=user_plan).first()
                medicines_text = ""
                
                for med in medicines:
                    med_line = f"• {med['name']}"
                    
                    # Add pricing for Pro and Deluxe plans
                    if user_plan in ['pro', 'deluxe'] and 'price' in med:
                        med_line += f" - {med['price']}"
                    
                    # Add purchase links for Deluxe plan only
                    if user_plan == 'deluxe' and 'buy_link' in med:
                        med_line += f" [Buy Now]({med['buy_link']})"
                    
                    medicines_text += med_line + "\n"
                
                # Filter medicine data for response
                if plan_data and plan_data.medicine_images:
                    # Keep all data for pro and deluxe plans
                    filtered_medicines = medicines
                else:
                    # Remove images for basic plan, keep pricing if available
                    filtered_medicines = []
                    for med in medicines:
                        filtered_med = {'name': med['name']}
                        if user_plan in ['pro', 'deluxe'] and 'price' in med:
                            filtered_med['price'] = med['price']
                        if user_plan == 'deluxe' and 'buy_link' in med:
                            filtered_med['buy_link'] = med['buy_link']
                        filtered_medicines.append(filtered_med)
                
                # Build localized response message
                symptoms_text = ', '.join(session_data['current_symptoms'])
                
                response_msg = get_localized_text('diagnosis_result', user_language,
                                                symptoms=symptoms_text,
                                                disease=disease_match['disease'],
                                                medicines=medicines_text.strip())
                
                # Add additional advice for deluxe plan
                if user_plan == 'deluxe':
                    advice = get_health_advice(disease_match['disease'])
                    advice_text = get_localized_text('health_advice', user_language, advice=advice)
                    response_msg += f"\n\n{advice_text}"
                
                return {
                    'message': response_msg,
                    'disease': disease_match['disease'],
                    'medicines': filtered_medicines
                }
            else:
                symptoms_text = ', '.join(session_data['current_symptoms'])
                return {
                    'message': get_localized_text('symptoms_noted', user_language, symptoms=symptoms_text)
                }
        else:
            symptoms_text = ', '.join(session_data['current_symptoms'])
            return {
                'message': get_localized_text('more_symptoms', user_language, symptoms=symptoms_text)
            }
    else:
        # No symptoms detected, ask for clarification
        if session_data['awaiting_symptoms']:
            return {
                'message': get_localized_text('no_symptoms_detected', user_language)
            }
        else:
            # Initial greeting
            session_data['awaiting_symptoms'] = True
            return {
                'message': get_localized_text('welcome_message', user_language)
            }

def get_health_advice(disease):
    """Get additional health advice for deluxe plan users"""
    advice_map = {
        'Common Cold': "• Stay hydrated by drinking plenty of fluids\n• Get adequate rest\n• Consider using a humidifier\n• Consult a doctor if symptoms persist beyond 10 days",
        'Fever': "• Stay hydrated with water and clear fluids\n• Rest in a cool environment\n• Monitor your temperature regularly\n• Seek medical attention if fever exceeds 103°F (39.4°C)",
        'Headache': "• Apply a cold or warm compress to your head\n• Stay hydrated\n• Try relaxation techniques\n• Avoid known triggers\n• See a doctor for severe or persistent headaches",
        'Stomach Upset': "• Eat bland foods like toast or rice\n• Stay hydrated with clear fluids\n• Avoid dairy and fatty foods\n• Rest and avoid strenuous activity\n• Consult a doctor if symptoms worsen",
        'Allergies': "• Avoid known allergens when possible\n• Keep windows closed during high pollen days\n• Shower after being outdoors\n• Use air purifiers indoors\n• Track your symptoms to identify triggers",
        'Cough': "• Stay hydrated to thin mucus\n• Use a humidifier or breathe steam\n• Avoid irritants like smoke\n• Try throat lozenges for sore throat\n• See a doctor if cough persists beyond 2 weeks"
    }
    return advice_map.get(disease, "• Follow medication instructions carefully\n• Stay hydrated and get adequate rest\n• Monitor your symptoms\n• Consult a healthcare professional if symptoms worsen")

@app.route('/usage_stats')
def usage_stats():
    """Get usage statistics for current user"""
    user_id = get_user_id()
    user_plan = get_user_plan()
    today = datetime.now().strftime('%Y-%m-%d')
    
    user = get_or_create_user(user_id)
    usage = DailyUsage.query.filter_by(user_id=user.id, date=today).first()
    current_usage = usage.chat_count if usage else 0
    
    plan_data = SubscriptionPlan.query.filter_by(plan_key=user_plan).first()
    max_chats = plan_data.max_chats_per_day if plan_data else 2
    
    return jsonify({
        'current_usage': current_usage,
        'max_chats': max_chats,
        'remaining': max_chats - current_usage if max_chats != 999 else 'unlimited'
    })

@app.errorhandler(404)
def not_found(error):
    # Provide default context for 404 pages
    user_id = get_user_id()
    user_plan = get_user_plan()
    available_languages = get_available_languages(user_plan)
    user_language = get_user_language()
    plans_data = get_plans_data()
    languages_data = load_languages()
    
    return render_template('index.html',
                         user_plan=user_plan,
                         user_language=user_language,
                         available_languages=available_languages,
                         plans=plans_data,
                         languages=languages_data), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error. Please try again later.'}), 500

# Initialize the application
with app.app_context():
    db.create_all()
    load_initial_data()
    init_symptom_matcher()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)