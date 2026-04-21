# AI SaaS Platform

A full-featured SaaS application with AI capabilities, built with Flask and PostgreSQL.

## Features

- User authentication with secure password hashing
- AI-powered chat interface with conversation history
- Prompt builder for structured AI interactions
- Project management for organizing AI work
- API key management for developer access
- Usage tracking and rate limiting

## Tech Stack

- **Backend**: Flask 3.0, SQLAlchemy, Flask-Migrate
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **AI**: OpenAI GPT-4, GPT-3.5 Turbo
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Containerization**: Docker, Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional for testing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/9KMan/JOB-20260419033041-c0d947.git
cd JOB-20260419033041-c0d947
```

2. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application at http://localhost:5000

## Development Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export FLASK_ENV=development
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saas_app_dev
export REDIS_URL=redis://localhost:6379/0
export SECRET_KEY=your-secret-key
export OPENAI_API_KEY=your-api-key
```

4. Initialize database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the development server:
```bash
python run.py
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Dashboard
- `GET /dashboard/` - Dashboard home
- `GET /dashboard/projects` - List projects
- `POST /dashboard/project/create` - Create project

### AI Features
- `GET /ai/chat` - Chat interface
- `POST /ai/api/chat` - Send chat message
- `POST /ai/api/prompt` - Execute prompt
- `GET /ai/api/models` - List available models

### User
- `GET /profile` - User profile
- `GET /api-keys` - API key management
- `POST /api-keys/create` - Create API key

## Configuration

Environment variables:
- `FLASK_ENV`: development/production/testing (default: development)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Flask secret key
- `OPENAI_API_KEY`: OpenAI API key
- `AI_MODEL`: Model to use (default: gpt-4-turbo-preview)
- `AI_TEMPERATURE`: Sampling temperature (default: 0.7)
- `AI_MAX_TOKENS`: Max response tokens (default: 2000)

## License

MIT License