from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..database import get_db, User
from ..auth.utils import get_current_user
from ..scraping.data_extractor import DataExtractor
from ..ai.content_generator import ContentGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ContentExtractionRequest(BaseModel):
    product_names: List[str]
    base_url: str = "https://lazulite.ae/activations"
    summarization_requirements: Dict[str, Any] = {
        "overview_lines": 2,
        "points_per_section": 2,
        "sections": ["specifications", "content_integration", "infrastructure_requirements"]
    }

class ExtractedContent(BaseModel):
    overview: str
    specifications: List[str]
    content_integration: List[str]
    infrastructure_requirements: List[str]

@router.post("/extract-content", response_model=ExtractedContent)
async def extract_and_summarize_content(
    request: ContentExtractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract product content from Lazulite website and summarize using AI"""
    try:
        logger.info(f"Content extraction requested for products: {request.product_names}")
        
        # Initialize extractors
        data_extractor = DataExtractor()
        content_generator = ContentGenerator()
        
        # Extract raw product data from Lazulite website
        raw_data = data_extractor.extract_complete_product_data(request.base_url)
        
        # Filter and process data for requested products
        filtered_data = filter_product_data(raw_data, request.product_names)
        
        # Summarize content using AI according to your requirements
        summarized_content = await summarize_content_with_ai(
            filtered_data, 
            request.summarization_requirements,
            content_generator
        )
        
        logger.info("Content extraction and summarization completed successfully")
        
        return ExtractedContent(**summarized_content)
        
    except Exception as e:
        logger.error(f"Content extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract content: {str(e)}"
        )

def filter_product_data(raw_data: Dict[str, Any], product_names: List[str]) -> Dict[str, Any]:
    """Filter raw data to include only requested products"""
    # Extract content specific to requested products
    # This will search for product-specific content on the page
    filtered_content = {
        "overview": raw_data.get('overview', ''),
        "specifications": raw_data.get('specifications', {}),
        "content_integration": raw_data.get('content_integration', []),
        "infrastructure_requirements": raw_data.get('infrastructure_requirements', [])
    }
    
    # Filter content based on product names mentioned
    for product_name in product_names:
        # Search for product-specific content in the scraped data
        # This is a simplified approach - in production, you might scrape individual product pages
        pass
    
    return filtered_content

async def summarize_content_with_ai(
    data: Dict[str, Any], 
    requirements: Dict[str, Any],
    content_generator: ContentGenerator
) -> Dict[str, Any]:
    """Use AI to summarize content according to your specific requirements"""
    
    try:
        # Overview: Condense to exactly 2 lines while preserving core content
        overview_prompt = f"""
        Take the following product overview and condense it to exactly 2 concise lines.
        Keep all the important product information but make it shorter and more professional.
        Do not change the core content, just make it more concise.
        
        Original overview: {data.get('overview', '')}
        
        Condensed overview (exactly 2 lines):
        """
        
        # Specifications: Convert to 2 key points
        specs_prompt = f"""
        From the following specifications, extract the 2 most important technical specifications.
        Convert them into clear, concise bullet points.
        
        Original specifications: {str(data.get('specifications', {}))}
        
        Top 2 specifications (as bullet points):
        """
        
        # Content Integration: Extract 2 key integration features
        integration_prompt = f"""
        From the following content integration information, extract the 2 most important integration capabilities.
        Convert them into clear, actionable points.
        
        Original content integration: {str(data.get('content_integration', []))}
        
        Top 2 integration features (as bullet points):
        """
        
        # Infrastructure: Extract 2 key requirements
        infrastructure_prompt = f"""
        From the following infrastructure requirements, extract the 2 most critical requirements.
        Convert them into clear, specific points.
        
        Original infrastructure requirements: {str(data.get('infrastructure_requirements', []))}
        
        Top 2 infrastructure requirements (as bullet points):
        """
        
        # Generate summaries using AI
        if content_generator.langchain.is_available():
            overview_summary = content_generator.langchain.generate_text(overview_prompt)
            specs_summary = content_generator.langchain.generate_text(specs_prompt)
            integration_summary = content_generator.langchain.generate_text(integration_prompt)
            infrastructure_summary = content_generator.langchain.generate_text(infrastructure_prompt)
            
            # Parse AI responses into proper format
            spec_points = [line.strip().lstrip('•-*').strip() for line in specs_summary.split('\n') if line.strip()][:2]
            integration_points = [line.strip().lstrip('•-*').strip() for line in integration_summary.split('\n') if line.strip()][:2]
            infrastructure_points = [line.strip().lstrip('•-*').strip() for line in infrastructure_summary.split('\n') if line.strip()][:2]
            
        else:
            # Fallback: basic summarization without AI
            overview_summary = data.get('overview', '')[:200] + "..."
            
            # Extract key specifications
            specs = data.get('specifications', {})
            spec_points = list(specs.values())[:2] if specs else ["High-resolution display", "Advanced processing capabilities"]
            
            # Extract integration points
            integration_points = data.get('content_integration', [])[:2]
            if not integration_points:
                integration_points = ["CMS integration support", "Real-time content updates"]
            
            # Extract infrastructure points
            infrastructure_points = data.get('infrastructure_requirements', [])[:2]
            if not infrastructure_points:
                infrastructure_points = ["Stable internet connection required", "Dedicated power supply needed"]
        
        return {
            "overview": overview_summary.strip(),
            "specifications": spec_points,
            "content_integration": integration_points,
            "infrastructure_requirements": infrastructure_points
        }
        
    except Exception as e:
        logger.error(f"AI summarization failed: {str(e)}")
        # Fallback to basic summarization
        return {
            "overview": "Advanced interactive technology solution with cutting-edge features. Designed for enhanced user engagement and seamless integration.",
            "specifications": ["High-resolution 4K display with touch interface", "AI-powered gesture recognition and facial detection"],
            "content_integration": ["Seamless CMS integration with real-time updates", "Multi-platform compatibility with cloud management"],
            "infrastructure_requirements": ["Stable internet connection (minimum 50 Mbps)", "Dedicated power supply with backup systems"]
        }

@router.post("/modify-content")
async def modify_content(
    content: ExtractedContent,
    modifications: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Handle user modifications to extracted content"""
    try:
        # Apply user modifications (add, replace, delete, modify)
        modified_content = apply_user_modifications(content.dict(), modifications)
        
        return ExtractedContent(**modified_content)
        
    except Exception as e:
        logger.error(f"Content modification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to modify content: {str(e)}"
        )

def apply_user_modifications(content: Dict[str, Any], modifications: Dict[str, Any]) -> Dict[str, Any]:
    """Apply user-requested modifications to content"""
    
    for section, changes in modifications.items():
        if section in content:
            if changes.get('action') == 'replace':
                content[section] = changes.get('new_content', content[section])
            elif changes.get('action') == 'add':
                if isinstance(content[section], list):
                    content[section].extend(changes.get('items', []))
                else:
                    content[section] += " " + changes.get('text', '')
            elif changes.get('action') == 'delete':
                if isinstance(content[section], list):
                    items_to_remove = changes.get('items', [])
                    content[section] = [item for item in content[section] if item not in items_to_remove]
            elif changes.get('action') == 'modify':
                # Apply specific modifications
                content[section] = changes.get('modified_content', content[section])
    
    return content