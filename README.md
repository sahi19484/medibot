# 🏥 HealthAssist - AI Medical Chatbot

An intelligent medical consultation chatbot built with Flask that provides symptom analysis, disease identification, and medicine recommendations through a subscription-based SaaS model.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🤖 AI-Powered Symptom Analysis
- Advanced symptom matching engine with keyword extraction and synonym recognition
- Intelligent disease identification from user-described symptoms
- Comprehensive disease database with medicine recommendations

### 💡 Subscription Plans
| Plan | Daily Chats | Bot Responses | Languages | Medicine Info | Purchase Links |
|------|-------------|---------------|-----------|---------------|----------------|
| **Basic** | 2 | 2 per chat | 2 (EN, HI) | Names only | ❌ |
| **Pro** | 5 | 4 per chat | 10 languages | Names + Pricing | ❌ |
| **Deluxe** | Unlimited | Unlimited | 60+ languages | Names + Pricing | ✅ 1mg.com |

### 🌐 Multi-Language Support
- **Basic Plan**: English, Hindi
- **Pro Plan**: English, Hindi, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean
- **Deluxe Plan**: 60+ languages including Chinese, Arabic, Turkish, Dutch, Swedish, and more
- Real-time language switching with localized responses

### 💊 Medicine Integration
- Medicine pricing information for Indian market (₹25-120 range)
- Direct purchase integration with 1mg.com pharmacy
- Visual medicine previews based on subscription tier

### 📱 Modern Web Interface
- Responsive chat interface with Bootstrap dark theme
- Real-time messaging with session persistence
- Interactive plan switching and language selection
- Sidebar navigation with usage tracking

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.1.1+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **Server**: Gunicorn WSGI server
- **AI Engine**: Custom symptom matching with keyword analysis

### Frontend
- **Templates**: Jinja2 with Bootstrap 5
- **Styling**: Custom CSS with dark theme
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JS for real-time interactions

### Dependencies
```
flask>=3.1.1
flask-sqlalchemy>=3.1.1
flask-migrate>=4.1.0
psycopg2-binary>=2.9.10
gunicorn>=23.0.0
email-validator>=2.2.0
trafilatura>=2.0.0
sqlalchemy>=2.0.41
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/healthassist-chatbot.git
cd healthassist-chatbot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
export DATABASE_URL="postgresql://username:password@localhost/healthassist"
export SESSION_SECRET="your-secret-key-here"
```

5. **Initialize database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Run the application**
```bash
python main.py
```

Visit `http://localhost:5000` to access the chatbot.

## 📊 Database Schema

### Core Models
- **User**: User management with subscription tracking and language preferences
- **ChatSession**: Conversation sessions with bot response counting
- **ChatMessage**: Individual messages with disease and medicine data
- **DailyUsage**: Usage tracking per user per day
- **Disease**: Disease database with symptoms and medicine mappings
- **SubscriptionPlan**: Plan configurations with feature matrices

### Key Relationships
```
User (1) ←→ (N) ChatSession ←→ (N) ChatMessage
User (1) ←→ (N) DailyUsage
SubscriptionPlan (1) ←→ (N) User
Disease (N) ←→ (N) ChatMessage
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session secret key

### Data Files
- `diseases_data.json`: Disease database with symptoms and medicines
- `plans.json`: Subscription plan configurations
- `languages.json`: Multi-language support data

## 🏗️ Architecture

### Core Components

1. **Symptom Matcher** (`model.py`)
   - AI-powered symptom analysis engine
   - Keyword extraction and synonym mapping
   - Disease matching algorithm

2. **Flask Application** (`app.py`)
   - Main web server and request handling
   - Session management and user tracking
   - Plan validation and usage limits

3. **Database Models** (`models.py`)
   - SQLAlchemy models for data persistence
   - Relationship management
   - Migration support

4. **Frontend Interface** (`templates/index.html`)
   - Interactive chat interface
   - Real-time messaging
   - Plan and language switching

### Data Flow
1. User submits symptoms through chat interface
2. System validates user plan and daily limits
3. SymptomMatcher processes and normalizes symptoms
4. Algorithm matches symptoms against disease database
5. System returns disease identification and medicine recommendations
6. Frontend displays results with plan-appropriate features

## 🔒 Security & Privacy

- Session-based user management with secure cookies
- Environment variable configuration for sensitive data
- Database-persisted user preferences and chat history
- Input validation and sanitization
- Plan-based feature access control

## 🧪 Testing

Run the application in development mode:
```bash
python main.py
```

The application includes:
- Automatic database initialization
- Sample data loading
- Debug logging enabled
- Hot reloading for development

## 🚀 Deployment

### Production Setup

1. **Set production environment variables**
```bash
export FLASK_ENV=production
export DATABASE_URL="your-production-db-url"
export SESSION_SECRET="strong-production-secret"
```

2. **Run with Gunicorn**
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### Deployment Considerations
- Use strong session secrets in production
- Configure proper database connection pooling
- Set up SSL/TLS for secure connections
- Implement proper logging and monitoring
- Consider load balancing for high traffic

## 📈 Usage Analytics

The application tracks:
- Daily chat usage per user
- Bot response counts per session
- Plan usage patterns
- Language preferences
- Disease query frequency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `replit.md`
- Review the database schema and API endpoints

## 🔮 Future Enhancements

- Voice chat integration
- Advanced AI models for better symptom analysis
- Integration with more pharmacy platforms
- Mobile app development
- Telemedicine video consultation
- Electronic health record integration

---

**Built with ❤️ for better healthcare accessibility**
