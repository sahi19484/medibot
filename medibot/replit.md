# AI Medical Chatbot - HealthAssist

## Overview

This is a Flask-based AI-powered medical chatbot that provides symptom analysis and medicine recommendations with a subscription-based SaaS model. The application allows users to describe their symptoms, matches them against a disease database, and provides medicine recommendations with optional image previews based on their subscription tier.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap dark theme
- **Styling**: Bootstrap 5 with custom CSS overrides
- **UI Components**: Responsive chat interface with sidebar navigation
- **Interactive Elements**: Real-time chat messaging, plan selection dropdown

### Backend Architecture
- **Framework**: Flask web framework with PostgreSQL database
- **Database**: PostgreSQL with Flask-SQLAlchemy ORM and Flask-Migrate for migrations
- **Session Management**: Flask sessions for user identification with database persistence
- **Data Storage**: PostgreSQL database for all persistent data (users, chats, diseases, plans)
- **API Structure**: RESTful endpoints for chat interactions and plan management

### Core Components
- **Symptom Matching Engine** (`model.py`): AI-powered symptom analysis using keyword matching and synonym recognition
- **Chat System**: Database-persisted conversation management with usage tracking
- **Subscription System**: Tiered plans with feature restrictions, daily limits, and language access stored in database
- **Multi-Language Support** (`languages.json`): Localized text and interface translations with plan-based language restrictions
- **Database Models** (`models.py`): SQLAlchemy models for Users, ChatSessions, ChatMessages, DailyUsage, Diseases, and SubscriptionPlans

## Key Components

### 1. Symptom Matcher (`model.py`)
- **Purpose**: Core AI engine for disease identification
- **Features**: 
  - Keyword-based symptom extraction
  - Synonym mapping for common symptom variations
  - Disease matching algorithm
- **Architecture**: Class-based design with configurable disease database

### 2. Flask Application (`app.py`)
- **Purpose**: Main web server and request handling
- **Features**:
  - Session management for user tracking
  - Daily usage limits per subscription plan
  - JSON data loading with error handling
- **Architecture**: Modular route handlers with middleware-like session management

### 3. Data Models
- **Diseases Database** (`diseases_data.json`): Structured symptom-to-disease mappings with medicine recommendations
- **Subscription Plans** (`plans.json`): Feature matrices for different pricing tiers

### 4. Frontend Interface (`templates/index.html`)
- **Purpose**: Interactive chat interface
- **Features**:
  - Real-time messaging
  - Plan switching capabilities
  - Responsive design with dark theme
- **Architecture**: Bootstrap-based responsive layout with custom CSS

## Data Flow

1. **User Interaction**: User submits symptoms through chat interface
2. **Session Validation**: System checks user plan and daily limits
3. **Symptom Processing**: SymptomMatcher extracts and normalizes symptoms
4. **Disease Matching**: Algorithm matches symptoms against disease database
5. **Response Generation**: System returns disease identification and medicine recommendations
6. **UI Update**: Frontend displays results with appropriate feature restrictions based on user plan

## External Dependencies

### Python Packages
- **Flask**: Web framework for HTTP handling and templating
- **Standard Libraries**: `json`, `logging`, `datetime`, `os` for core functionality

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome 6.4.0**: Icon library for UI elements
- **Replit Bootstrap Theme**: Custom dark theme styling

### Data Dependencies
- **Disease Database**: Local JSON file with symptom-disease mappings
- **Medicine Images**: SVG/PNG assets stored in static directory
- **Subscription Plans**: JSON configuration for feature management

## Deployment Strategy

### Local Development
- **Entry Point**: `main.py` for development server
- **Configuration**: Environment variables for session secrets
- **Debug Mode**: Enabled for development with hot reloading

### Production Considerations
- **Security**: Session secret should be environment-configurable
- **Logging**: Structured logging with configurable levels
- **Static Assets**: Medicine images served through Flask static file handler
- **Session Storage**: In-memory storage suitable for single-instance deployment

## User Preferences

Preferred communication style: Simple, everyday language.

## Language Support

### Plan-Based Language Access
- **Basic Plan**: 2 languages (English, Hindi)
- **Pro Plan**: 10 languages (English, Hindi, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean)
- **Deluxe Plan**: 60+ languages (includes all Pro languages plus Chinese, Arabic, Turkish, Dutch, Swedish, and many more)

### Implementation Details
- Language preferences stored in database per user
- Localized bot responses based on user's selected language
- Plan validation ensures users can only select languages available in their subscription tier
- Language switching triggers interface reload to apply translations

## Medicine Pricing and Purchase Integration

### Plan-Based Medicine Information Access
- **Basic Plan**: Medicine names only
- **Pro Plan**: Medicine names + pricing information
- **Deluxe Plan**: Medicine names + pricing + direct purchase links to 1mg.com

### Implementation Details
- Medicine data includes price ranges for Indian market (₹25-120 range)
- Purchase links integrate with 1mg online pharmacy platform
- Pricing and links filtered based on user subscription tier
- Enhanced medicine display with visual pricing and purchase buttons

## Chat Limits and Bot Response Restrictions

### Plan-Based Chat Limitations
- **Basic Plan**: 2 chats per day, 2 bot responses per chat, English only
- **Pro Plan**: 5 chats per day, 4 bot responses per chat, any 2 languages
- **Deluxe Plan**: Unlimited chats and bot responses, all 60+ languages

### Implementation Details
- Chat session tracking with bot response counters
- Automatic limit enforcement with clear user notifications
- "New Chat" functionality to start fresh sessions
- Real-time response limit display in sidebar
- Daily usage tracking per subscription plan

## Changelog

Changelog:
- June 29, 2025. Initial setup with PostgreSQL database integration
- June 29, 2025. Added multi-language support with plan-based language restrictions
- June 29, 2025. Implemented medicine pricing and purchase links with 1mg integration
- June 29, 2025. Added comprehensive chat limits and bot response restrictions per plan