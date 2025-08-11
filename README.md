# Lazulite AI PPT Generator

AI-powered PowerPoint generation system that extracts product data from Lazulite website and creates professional presentations with user approval workflow.

## 🚀 Features

- **Smart Content Extraction**: Automatically extracts product information from https://lazulite.ae/activations
- **AI-Powered Summarization**: Condenses lengthy content into concise, professional format
- **User Approval Workflow**: Review and modify extracted content before PPT generation
- **Interactive Chat Interface**: Natural language interaction for content modifications
- **Professional PPT Generation**: Creates branded PowerPoint presentations
- **Real-time Processing**: Background task processing with status updates

## 📋 Content Format

The system extracts and formats content as follows:

### Overview
- **2 lines maximum** - AI-condensed while preserving core product information

### Specifications
- **2 key points** - Most important technical specifications

### Content Integration
- **2 key points** - Primary integration capabilities and features

### Infrastructure Requirements
- **2 key points** - Critical setup and operational requirements

## 🛠️ Setup Instructions

### Prerequisites

- **Node.js 18+** (for frontend)
- **Python 3.9+** (for backend)
- **PostgreSQL 13+** (database)
- **Redis 6+** (task queue)
- **Chrome/Chromium** (for web scraping)

### Frontend Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Run automated setup**
   ```bash
   python setup_backend.py
   ```

3. **Manual setup (alternative)**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup configuration
   cp .env.example .env
   # Edit .env with your settings
   
   # Create database
   createdb lazulite_ppt
   
   # Run migrations
   alembic upgrade head
   ```

4. **Start services**
   ```bash
   # Terminal 1: API Server
   python run_dev.py
   
   # Terminal 2: Background Worker
   python run_worker.py
   
   # Terminal 3: Task Scheduler (optional)
   python run_beat.py
   ```

## 🔧 Configuration

### Environment Variables

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

**Backend (.env)**
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lazulite_ppt

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (for AI features)
OPENAI_API_KEY=your_openai_api_key

# Lazulite Website
LAZULITE_BASE_URL=https://lazulite.ae/activations

# Security
SECRET_KEY=your-very-long-secret-key
```

## 🎯 Usage Workflow

### 1. Content Extraction
```
User Input: "Generate PPT for Open House Event on August 11, 2025 in Dubai 
featuring salesperson Jasmeet Kaur with products: AI Photobooth, Kinetic Ceiling"

System: Extracts content from https://lazulite.ae/activations
```

### 2. Content Review & Approval
```
System: Shows extracted content in structured format
- Overview (2 lines)
- Specifications (2 points)
- Content Integration (2 points)
- Infrastructure Requirements (2 points)

User: Can approve, edit, or request modifications
```

### 3. Content Modification Commands
```
"Add more details about installation"
"Replace the first specification with..."
"Delete the second infrastructure requirement"
"Modify the overview to include..."
```

### 4. PPT Generation
```
System: Generates professional PowerPoint with:
- Title slide with event details
- Product overview slides
- Specification slides
- Integration capability slides
- Infrastructure requirement slides
- Conclusion slide
```

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Hook Form** for form management
- **Lucide React** for icons

### Backend (Python + FastAPI)
- **FastAPI** for API framework
- **SQLAlchemy** for database ORM
- **Celery** for background tasks
- **Selenium** for web scraping
- **LangChain** for AI integration
- **python-pptx** for PPT generation

### Key Components
- **Web Scraper**: Extracts content from Lazulite website
- **AI Processor**: Summarizes and formats content
- **PPT Generator**: Creates branded presentations
- **Chat System**: Handles user interactions
- **Task Queue**: Manages background processing

## 🔍 API Endpoints

### Content Extraction
```http
POST /api/extract-content
{
  "product_names": ["AI Photobooth", "Kinetic Ceiling"],
  "base_url": "https://lazulite.ae/activations",
  "summarization_requirements": {
    "overview_lines": 2,
    "points_per_section": 2
  }
}
```

### PPT Generation
```http
POST /api/ppt/generate
{
  "prompt": "Generate PPT for event...",
  "approved_content": { ... }
}
```

### Content Modification
```http
POST /api/modify-content
{
  "content": { ... },
  "modifications": {
    "overview": {
      "action": "replace",
      "new_content": "Updated overview text"
    }
  }
}
```

## 🚦 Development Mode

The system includes a development mode that:
- Uses simulated data when backend is unavailable
- Provides realistic demo responses
- Allows frontend development without full backend setup

## 📊 Monitoring

### Health Checks
- **API Health**: `GET /health`
- **Database Status**: Included in health check
- **AI Service Status**: Included in health check

### Logging
- Structured logging with different levels
- Request/response logging
- Error tracking and reporting

## 🔒 Security

- JWT-based authentication
- Input validation and sanitization
- SQL injection protection
- File upload security
- CORS configuration

## 🚀 Deployment

### Docker Deployment
```bash
cd backend
docker-compose up -d
```

### Manual Deployment
1. Set up production database
2. Configure environment variables
3. Run database migrations
4. Start API server and workers
5. Configure reverse proxy (nginx)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: info@lazulite.ae
- Documentation: [API Docs](http://localhost:8000/docs)