# Lazulite AI PPT Generator - Backend

AI-powered PowerPoint generation system that extracts product data from Lazulite website and creates professional presentations using advanced AI content enhancement.

## 🚀 Features

- **Web Scraping**: Automated extraction of product data from Lazulite website
- **AI Content Enhancement**: Uses OpenAI GPT models to improve and format content
- **PPT Generation**: Creates professional PowerPoint presentations with custom templates
- **Image Processing**: Converts WebP images to PPT-compatible formats
- **Background Processing**: Celery-based task queue for handling long-running operations
- **RESTful API**: FastAPI-based API with automatic documentation
- **Authentication**: JWT-based user authentication and authorization
- **Chat Interface**: Interactive chat for PPT generation requests
- **File Management**: Secure file upload, storage, and download

## 🏗️ Architecture

### Technology Stack

- **Python 3.9+** - Main backend language
- **FastAPI** - Modern web framework for building APIs
- **LangChain** - AI/LLM integration and prompt management
- **OpenAI GPT-4** - Intelligent content generation
- **Celery** - Background task processing
- **Redis** - Task queue and caching
- **PostgreSQL** - Database for user data and chat history
- **Docker** - Containerization

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and models
│   ├── auth/                  # Authentication module
│   ├── scraping/              # Web scraping module
│   ├── ppt/                   # PPT generation module
│   ├── ai/                    # AI integration module
│   ├── api/                   # API endpoints
│   ├── tasks/                 # Background tasks
│   └── utils/                 # Utility functions
├── templates/                 # PPT templates
├── uploads/                   # Temporary file storage
├── generated/                 # Generated PPT files
├── alembic/                   # Database migrations
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Docker image
└── requirements.txt           # Python dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Chrome/Chromium (for web scraping)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
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
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb lazulite_ppt
   
   # Run migrations
   alembic upgrade head
   ```

6. **Start Redis**
   ```bash
   redis-server
   ```

7. **Run the application**
   ```bash
   # Terminal 1: API Server
   python run_dev.py
   
   # Terminal 2: Celery Worker
   python run_worker.py
   
   # Terminal 3: Celery Beat (optional, for periodic tasks)
   python run_beat.py
   ```

### Docker Setup

1. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lazulite_ppt

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# JWT
SECRET_KEY=your-secret-key-change-in-production

# File Storage
UPLOAD_DIR=uploads
GENERATED_DIR=generated
TEMPLATE_DIR=templates
```

### Database Migration

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

#### PPT Generation
- `POST /api/ppt/generate` - Generate PPT from prompt
- `GET /api/ppt/status/{task_id}` - Check generation status
- `GET /api/ppt/download/{filename}` - Download generated PPT
- `GET /api/ppt/history` - Get generation history

#### Chat
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions` - Get chat sessions
- `POST /api/chat/sessions/{session_id}/messages` - Send message
- `GET /api/chat/sessions/{session_id}/messages` - Get messages

#### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `POST /api/user/change-password` - Change password
- `GET /api/user/stats` - Get user statistics

## 🔄 Background Tasks

The system uses Celery for background processing:

### PPT Generation Task
- Scrapes product data from Lazulite website
- Processes and converts images
- Enhances content using AI
- Generates PowerPoint presentation
- Provides real-time progress updates

### Maintenance Tasks
- Cleanup old files
- Database maintenance
- Health checks

### Monitoring Tasks

```bash
# Monitor Celery workers
celery -A app.tasks.celery_app inspect active

# Monitor task queue
celery -A app.tasks.celery_app inspect reserved

# Flower monitoring (install flower first)
pip install flower
celery -A app.tasks.celery_app flower
```

## 🧪 Testing

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run tests with verbose output
pytest -v
```

## 🚀 Deployment

### Production Deployment with Docker

1. **Set production environment variables**
   ```bash
   export ENVIRONMENT=production
   export DEBUG=false
   export SECRET_KEY=your-production-secret-key
   export OPENAI_API_KEY=your-openai-api-key
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Run database migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. **Set up SSL (recommended)**
   - Configure SSL certificates in nginx.conf
   - Update CORS settings for production domain

### Health Checks

The application provides health check endpoints:

- `GET /health` - Overall system health
- `GET /health/db` - Database connectivity
- `GET /health/redis` - Redis connectivity
- `GET /health/ai` - AI service availability

## 📊 Monitoring and Logging

### Logging

Logs are configured with different levels:
- **INFO**: General application flow
- **WARNING**: Potential issues
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging information

### Metrics

Key metrics to monitor:
- API response times
- Task queue length
- Database connection pool
- Memory and CPU usage
- PPT generation success rate

## 🔒 Security

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Token expiration and refresh

### File Security
- File type validation
- Size limits
- Path traversal protection
- Secure file storage

### API Security
- CORS configuration
- Rate limiting
- Input validation
- SQL injection protection

## 🐛 Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Issues**
   ```bash
   # Install Chrome dependencies
   sudo apt-get update
   sudo apt-get install -y google-chrome-stable
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Test connection
   psql -h localhost -U user -d lazulite_ppt
   ```

3. **Redis Connection Issues**
   ```bash
   # Check Redis status
   redis-cli ping
   
   # Start Redis
   redis-server
   ```

4. **Celery Worker Issues**
   ```bash
   # Check worker status
   celery -A app.tasks.celery_app inspect ping
   
   # Restart workers
   pkill -f celery
   python run_worker.py
   ```

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: info@lazulite.ae
- Documentation: [API Docs](http://localhost:8000/docs)

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Complete PPT generation pipeline
- AI content enhancement
- Web scraping capabilities
- User authentication
- Chat interface
- Background task processing