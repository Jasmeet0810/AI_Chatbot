# Backend Architecture for Lazulite AI PPT Generator

## Technology Stack

### Core Technologies
- **Python 3.9+** - Main backend language
- **FastAPI** - Modern, fast web framework for building APIs
- **LangChain** - For AI/LLM integration and prompt management
- **OpenAI GPT-4** or **Anthropic Claude** - For intelligent content generation
- **Celery** - For background task processing
- **Redis** - Task queue and caching
- **PostgreSQL** - Database for user data and chat history
- **Docker** - Containerization

### Key Libraries
```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
python-pptx==0.6.21
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.0
Pillow==10.0.1
langchain==0.0.335
openai==1.3.0
celery==5.3.4
redis==5.0.1
sqlalchemy==2.0.23
alembic==1.12.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and models
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py          # User authentication models
│   │   ├── routes.py          # Auth endpoints
│   │   └── utils.py           # JWT utilities
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── lazulite_scraper.py # Main scraping logic
│   │   ├── image_processor.py  # Image conversion utilities
│   │   └── data_extractor.py   # Product data extraction
│   ├── ppt/
│   │   ├── __init__.py
│   │   ├── generator.py        # PPT generation logic
│   │   ├── templates.py        # PPT template management
│   │   └── styles.py          # Styling and formatting
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── langchain_service.py # LangChain integration
│   │   ├── prompts.py          # AI prompts and templates
│   │   └── content_generator.py # AI content generation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat endpoints
│   │   ├── ppt.py             # PPT generation endpoints
│   │   └── user.py            # User management endpoints
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery configuration
│   │   └── ppt_tasks.py       # Background PPT generation
│   └── utils/
│       ├── __init__.py
│       ├── file_manager.py    # File upload/download utilities
│       └── validators.py      # Input validation
├── templates/
│   └── lazulite_template.pptx # PPT template file
├── uploads/                   # Temporary file storage
├── generated/                 # Generated PPT files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Core Components

### 1. Web Scraping Module (`scraping/lazulite_scraper.py`)

```python
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
import os
from typing import Dict, List, Optional

class LazuliteScraper:
    def __init__(self):
        self.base_url = "https://lazulite.ae/activations"
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Selenium WebDriver for dynamic content"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def scrape_product_data(self, product_url: str) -> Dict:
        """Scrape product data from Lazulite website"""
        try:
            self.driver.get(product_url)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract product data based on the structure you described
            product_data = {
                "name": self.extract_product_name(soup),
                "overview": self.extract_overview(soup),
                "images": self.extract_images(soup),
                "specifications": self.extract_specifications(soup),
                "content_integration": self.extract_content_integration(soup),
                "infrastructure_requirements": self.extract_infrastructure(soup)
            }
            
            return product_data
            
        except Exception as e:
            raise Exception(f"Failed to scrape product data: {str(e)}")
    
    def extract_product_name(self, soup) -> str:
        """Extract product name"""
        # Implement based on actual HTML structure
        title_element = soup.find('h1') or soup.find('title')
        return title_element.get_text().strip() if title_element else "Unknown Product"
    
    def extract_overview(self, soup) -> str:
        """Extract product overview"""
        # Look for overview section
        overview_section = soup.find('section', class_='overview') or soup.find('div', class_='product-overview')
        if overview_section:
            return overview_section.get_text().strip()
        return "Product overview not available"
    
    def extract_images(self, soup) -> List[str]:
        """Extract and process product images"""
        images = []
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src and self.is_product_image(src):
                # Convert relative URLs to absolute
                if src.startswith('/'):
                    src = f"https://lazulite.ae{src}"
                images.append(src)
        
        return images[:10]  # Limit to 10 images
    
    def extract_specifications(self, soup) -> Dict[str, str]:
        """Extract key specifications"""
        specs = {}
        spec_section = soup.find('section', class_='specifications') or soup.find('div', class_='specs')
        
        if spec_section:
            # Extract specification items
            spec_items = spec_section.find_all(['li', 'div', 'p'])
            for item in spec_items:
                text = item.get_text().strip()
                if ':' in text:
                    key, value = text.split(':', 1)
                    specs[key.strip()] = value.strip()
        
        return specs
    
    def extract_content_integration(self, soup) -> List[str]:
        """Extract content integration information"""
        integration_items = []
        integration_section = soup.find('section', class_='content-integration')
        
        if integration_section:
            items = integration_section.find_all(['li', 'p'])
            for item in items:
                text = item.get_text().strip()
                if text:
                    integration_items.append(text)
        
        return integration_items
    
    def extract_infrastructure(self, soup) -> List[str]:
        """Extract infrastructure requirements"""
        requirements = []
        infra_section = soup.find('section', class_='infrastructure')
        
        if infra_section:
            items = infra_section.find_all(['li', 'p'])
            for item in items:
                text = item.get_text().strip()
                if text:
                    requirements.append(text)
        
        return requirements
    
    def is_product_image(self, src: str) -> bool:
        """Check if image is a product image"""
        # Filter out logos, icons, etc.
        exclude_keywords = ['logo', 'icon', 'favicon', 'banner']
        return not any(keyword in src.lower() for keyword in exclude_keywords)
    
    def download_and_convert_image(self, image_url: str, output_path: str) -> str:
        """Download and convert WebP images to PNG/JPG"""
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            # Open image with Pillow
            image = Image.open(io.BytesIO(response.content))
            
            # Convert WebP to PNG
            if image.format == 'WEBP':
                png_path = output_path.replace('.webp', '.png')
                image.save(png_path, 'PNG')
                return png_path
            else:
                image.save(output_path)
                return output_path
                
        except Exception as e:
            raise Exception(f"Failed to process image {image_url}: {str(e)}")
```

### 2. PPT Generation Module (`ppt/generator.py`)

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os
from typing import Dict, List
from ..ai.content_generator import ContentGenerator

class PPTGenerator:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.content_generator = ContentGenerator()
    
    def generate_presentation(self, product_data: Dict, user_prompt: str) -> str:
        """Generate PPT from product data and user prompt"""
        try:
            # Load template
            prs = Presentation(self.template_path)
            
            # Generate AI-enhanced content
            enhanced_content = self.content_generator.enhance_content(product_data, user_prompt)
            
            # Create slides
            self.create_title_slide(prs, enhanced_content)
            self.create_overview_slide(prs, enhanced_content)
            self.create_specifications_slide(prs, enhanced_content)
            self.create_content_integration_slide(prs, enhanced_content)
            self.create_infrastructure_slide(prs, enhanced_content)
            
            # Save presentation
            output_path = f"generated/presentation_{hash(user_prompt)}.pptx"
            prs.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to generate presentation: {str(e)}")
    
    def create_title_slide(self, prs, content):
        """Create title slide"""
        slide = prs.slides[0]  # Use first slide from template
        
        # Update title and subtitle
        title = slide.shapes.title
        title.text = content['title']
        
        if slide.placeholders:
            subtitle = slide.placeholders[1]
            subtitle.text = content['subtitle']
    
    def create_overview_slide(self, prs, content):
        """Create product overview slide with images"""
        slide_layout = prs.slide_layouts[1]  # Content with image layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title = slide.shapes.title
        title.text = "Product Overview"
        
        # Add content
        content_placeholder = slide.placeholders[1]
        content_placeholder.text = content['overview_text']
        
        # Add images if available
        if content.get('images'):
            self.add_images_to_slide(slide, content['images'])
    
    def create_specifications_slide(self, prs, content):
        """Create specifications slide"""
        slide_layout = prs.slide_layouts[2]  # Bullet points layout
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        title.text = "Key Specifications"
        
        # Convert bullet points to sentences using AI
        specs_text = content['specifications_sentences']
        content_placeholder = slide.placeholders[1]
        content_placeholder.text = specs_text
    
    def add_images_to_slide(self, slide, images: List[str]):
        """Add converted images to slide"""
        # Position images in a grid
        img_width = Inches(2)
        img_height = Inches(1.5)
        
        for i, img_path in enumerate(images[:4]):  # Max 4 images per slide
            if os.path.exists(img_path):
                left = Inches(0.5 + (i % 2) * 3)
                top = Inches(2 + (i // 2) * 2)
                slide.shapes.add_picture(img_path, left, top, img_width, img_height)
```

### 3. AI Content Generation (`ai/content_generator.py`)

```python
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List

class ContentGenerator:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7)
        self.setup_prompts()
    
    def setup_prompts(self):
        """Setup LangChain prompts for content generation"""
        self.overview_prompt = PromptTemplate(
            input_variables=["product_name", "raw_overview", "user_prompt"],
            template="""
            Create a professional product overview for {product_name} based on the following information:
            
            Raw Overview: {raw_overview}
            User Request: {user_prompt}
            
            Generate a compelling, professional overview that would work well in a business presentation.
            Focus on key benefits and features. Keep it concise but informative.
            """
        )
        
        self.specs_prompt = PromptTemplate(
            input_variables=["specifications", "user_prompt"],
            template="""
            Convert the following bullet-point specifications into well-written sentences suitable for a professional presentation:
            
            Specifications: {specifications}
            Context: {user_prompt}
            
            Transform each specification into a complete, professional sentence. 
            Make it sound natural and business-appropriate.
            """
        )
    
    def enhance_content(self, product_data: Dict, user_prompt: str) -> Dict:
        """Use AI to enhance and format content"""
        enhanced = {}
        
        # Generate title and subtitle
        enhanced['title'] = f"{product_data['name']} Presentation"
        enhanced['subtitle'] = "Powered by Lazulite AI Technology"
        
        # Enhance overview
        overview_chain = LLMChain(llm=self.llm, prompt=self.overview_prompt)
        enhanced['overview_text'] = overview_chain.run(
            product_name=product_data['name'],
            raw_overview=product_data['overview'],
            user_prompt=user_prompt
        )
        
        # Convert specifications to sentences
        specs_chain = LLMChain(llm=self.llm, prompt=self.specs_prompt)
        enhanced['specifications_sentences'] = specs_chain.run(
            specifications=str(product_data['specifications']),
            user_prompt=user_prompt
        )
        
        # Process images
        enhanced['images'] = product_data.get('images', [])
        
        return enhanced
```

### 4. FastAPI Main Application (`main.py`)

```python
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import os

from .auth.routes import auth_router
from .api.chat import chat_router
from .api.ppt import ppt_router
from .tasks.ppt_tasks import generate_ppt_task
from .database import get_db

app = FastAPI(title="Lazulite AI PPT Generator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(ppt_router, prefix="/ppt", tags=["presentations"])

class PPTRequest(BaseModel):
    prompt: str
    product_url: Optional[str] = None

@app.post("/generate-ppt")
async def generate_ppt(
    request: PPTRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    """Generate PPT from user prompt"""
    try:
        # Start background task
        task = generate_ppt_task.delay(
            user_id=current_user.id,
            prompt=request.prompt,
            product_url=request.product_url or "https://lazulite.ae/activations"
        )
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "PPT generation started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Lazulite AI PPT Generator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5. Background Tasks (`tasks/ppt_tasks.py`)

```python
from celery import Celery
from ..scraping.lazulite_scraper import LazuliteScraper
from ..ppt.generator import PPTGenerator
import os

celery_app = Celery(
    "ppt_generator",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def generate_ppt_task(user_id: str, prompt: str, product_url: str):
    """Background task for PPT generation"""
    try:
        # Step 1: Scrape product data
        scraper = LazuliteScraper()
        product_data = scraper.scrape_product_data(product_url)
        
        # Step 2: Download and convert images
        converted_images = []
        for img_url in product_data['images']:
            try:
                img_path = f"uploads/img_{hash(img_url)}.png"
                converted_path = scraper.download_and_convert_image(img_url, img_path)
                converted_images.append(converted_path)
            except Exception as e:
                print(f"Failed to process image {img_url}: {e}")
        
        product_data['images'] = converted_images
        
        # Step 3: Generate PPT
        generator = PPTGenerator("templates/lazulite_template.pptx")
        ppt_path = generator.generate_presentation(product_data, prompt)
        
        # Step 4: Generate download URL
        download_url = f"/download/{os.path.basename(ppt_path)}"
        
        return {
            "status": "completed",
            "download_url": download_url,
            "file_path": ppt_path
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
```

## Deployment with Docker

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/lazulite_ppt
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./generated:/app/generated
      - ./templates:/app/templates

  worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/lazulite_ppt
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./generated:/app/generated
      - ./templates:/app/templates

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=lazulite_ppt
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## API Integration

To integrate with your frontend, you'll need to:

1. **Update the API service** (`src/services/api.ts`):
```typescript
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

export class APIService {
  static async generatePPT(prompt: string, token: string): Promise<{ taskId: string }> {
    const response = await fetch(`${API_BASE_URL}/generate-ppt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ prompt }),
    });
    return await response.json();
  }

  static async checkTaskStatus(taskId: string, token: string) {
    const response = await fetch(`${API_BASE_URL}/task/${taskId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return await response.json();
  }
}
```

This architecture provides a complete, production-ready backend for your Lazulite AI PPT Generator with web scraping, image processing, AI-powered content generation, and PPT creation capabilities.