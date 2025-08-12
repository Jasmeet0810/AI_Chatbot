# Lazulite AI PPT Generator - Backend

AI-powered PowerPoint generation system that extracts product data from Lazulite website and creates professional presentations using AWS Bedrock Claude.

## 🚀 Features

- **Web Scraping**: Automated extraction of product data from Lazulite website
- **AI Content Enhancement**: Uses AWS Bedrock Claude to improve and format content
- **PPT Generation**: Creates professional PowerPoint presentations with custom templates
- **Image Processing**: Converts WebP images to PPT-compatible formats
- **RESTful API**: FastAPI-based API with automatic documentation
- **No Authentication**: Simplified for direct usage

## 🏗️ Architecture

### Technology Stack

- **Python 3.9+** - Main backend language
- **FastAPI** - Modern web framework for building APIs
- **AWS Bedrock Claude** - AI content generation and enhancement
- **Selenium** - Web scraping for dynamic content
- **python-pptx** - PowerPoint generation
- **Pillow** - Image processing

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── scraping/              # Web scraping module
│   ├── ppt/                   # PPT generation module
│   ├── ai/                    # AI integration module (Bedrock Claude)
│   ├── api/                   # API endpoints
│   └── utils/                 # Utility functions
├── templates/                 # PPT templates
├── uploads/                   # Temporary file storage
├── generated/                 # Generated PPT files
└── requirements.txt           # Python dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- Chrome/Chromium (for web scraping)
- AWS Account with Bedrock access

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
   # Edit .env with your AWS credentials
   ```

5. **Run the application**
   ```bash
   python run_dev.py
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# AWS Bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# File Storage
UPLOAD_DIR=uploads
GENERATED_DIR=generated
TEMPLATE_DIR=templates

# Scraping
LAZULITE_BASE_URL=https://lazulite.ae/activations
SELENIUM_TIMEOUT=30
MAX_IMAGES_PER_PRODUCT=10
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Key Endpoints

#### Content Extraction
- `POST /api/extract-content` - Extract and enhance product content
- `POST /api/modify-content` - Modify extracted content

#### PPT Generation
- `POST /api/ppt/generate` - Generate PPT from approved content
- `GET /api/ppt/status/{task_id}` - Check generation status
- `GET /api/ppt/download/{filename}` - Download generated PPT

## 🎯 Usage Workflow

### 1. Content Extraction
```bash
POST /api/extract-content
{
  "product_names": ["AI Photobooth", "Kinetic Ceiling"],
  "base_url": "https://lazulite.ae/activations"
}
```

### 2. Content Enhancement
The system automatically uses AWS Bedrock Claude to:
- Summarize content to exactly 2 lines for overview
- Extract 2 key specifications
- Identify 2 main integration features
- List 2 critical infrastructure requirements

### 3. PPT Generation
```bash
POST /api/ppt/generate
{
  "prompt": "Generate PPT for Open House Event...",
  "approved_content": [...]
}
```

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
   ```bash
   export ENVIRONMENT=production
   export DEBUG=false
   export AWS_ACCESS_KEY_ID=your-production-key
   export AWS_SECRET_ACCESS_KEY=your-production-secret
   ```

2. **Run with production server**
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## 🔍 Health Checks

The application provides health check endpoints:

- `GET /health` - Overall system health
- Checks AI service availability (AWS Bedrock)
- Verifies file system access

## 🐛 Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Issues**
   ```bash
   # Install Chrome dependencies
   sudo apt-get update
   sudo apt-get install -y google-chrome-stable
   ```

2. **AWS Bedrock Access Issues**
   - Ensure your AWS credentials have Bedrock access
   - Check if Claude model is available in your region
   - Verify AWS_REGION is set correctly

3. **File Permission Issues**
   ```bash
   # Ensure directories are writable
   chmod 755 uploads generated templates
   ```

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: info@lazulite.ae
- Documentation: [API Docs](http://localhost:8000/docs)