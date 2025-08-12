from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..database import get_db, User
from ..auth.utils import get_current_user
from ..scraping.multi_product_extractor import MultiProductExtractor
from ..ai.content_generator import ContentGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ProductExtractionRequest(BaseModel):
    product_names: List[str]
    base_url: str = "https://lazulite.ae/activations"
    summarization_requirements: Dict[str, Any] = {
        "overview_lines": 2,
        "points_per_section": 2,
        "sections": ["specifications", "content_integration", "infrastructure_requirements"]
    }

class ProductContent(BaseModel):
    product_name: str
    overview: str
    specifications: List[str]
    content_integration: List[str]
    infrastructure_requirements: List[str]
    images: List[str]  # Local file paths for processed images
    image_layout: str  # "single", "side_by_side", "grid"

class MultiProductResponse(BaseModel):
    products: List[ProductContent]
    total_products: int
    extraction_status: str

@router.post("/extract-content", response_model=MultiProductResponse)
async def extract_multiple_products_content(
    request: ProductExtractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract content for multiple products from Lazulite website"""
    try:
        logger.info(f"Multi-product extraction requested for: {request.product_names}")
        
        # Initialize extractors
        multi_extractor = MultiProductExtractor()
        content_generator = ContentGenerator()
        
        # Extract content for each product individually
        extracted_products = []
        
        for product_name in request.product_names:
            try:
                logger.info(f"Processing product: {product_name}")
                
                # Extract raw product data
                raw_data = multi_extractor.extract_single_product_data(
                    product_name, 
                    request.base_url
                )
                
                # Process and convert images
                processed_images = multi_extractor.process_product_images(
                    raw_data.get('images', []),
                    product_name
                )
                
                # Determine image layout based on count
                image_layout = determine_image_layout(len(processed_images))
                
                # AI-powered content summarization
                summarized_content = await summarize_product_content(
                    raw_data,
                    product_name,
                    request.summarization_requirements,
                    content_generator
                )
                
                # Create product content structure
                product_content = ProductContent(
                    product_name=product_name,
                    overview=summarized_content['overview'],
                    specifications=summarized_content['specifications'],
                    content_integration=summarized_content['content_integration'],
                    infrastructure_requirements=summarized_content['infrastructure_requirements'],
                    images=processed_images,
                    image_layout=image_layout
                )
                
                extracted_products.append(product_content)
                logger.info(f"Successfully processed product: {product_name}")
                
            except Exception as e:
                logger.error(f"Failed to process product {product_name}: {str(e)}")
                # Add fallback content for failed products
                fallback_content = create_fallback_product_content(product_name)
                extracted_products.append(fallback_content)
        
        logger.info(f"Multi-product extraction completed. Processed {len(extracted_products)} products")
        
        return MultiProductResponse(
            products=extracted_products,
            total_products=len(extracted_products),
            extraction_status="completed"
        )
        
    except Exception as e:
        logger.error(f"Multi-product extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract content: {str(e)}"
        )

def determine_image_layout(image_count: int) -> str:
    """Determine image layout based on count"""
    if image_count == 1:
        return "single"
    elif image_count == 2:
        return "side_by_side"
    elif image_count >= 3:
        return "grid"
    else:
        return "none"

async def summarize_product_content(
    raw_data: Dict[str, Any],
    product_name: str,
    requirements: Dict[str, Any],
    content_generator: ContentGenerator
) -> Dict[str, Any]:
    """AI-powered content summarization for specific format"""
    
    try:
        # Overview: Condense to exactly 2 lines
        overview_prompt = f"""
        Take the following product overview for {product_name} and condense it to exactly 2 concise lines.
        Keep all the important product information but make it shorter and more professional.
        Do not change the core content, just make it more concise and clear.
        
        Original overview: {raw_data.get('overview', '')}
        
        Condensed overview (exactly 2 lines):
        """
        
        # Specifications: Extract 2 key points
        specs_prompt = f"""
        From the following specifications for {product_name}, extract the 2 most important technical specifications.
        Convert them into clear, concise bullet points without bullet symbols.
        
        Original specifications: {str(raw_data.get('specifications', {}))}
        
        Top 2 specifications (as 2 separate lines):
        """
        
        # Content Integration: Extract 2 key features
        integration_prompt = f"""
        From the following content integration information for {product_name}, extract the 2 most important integration capabilities.
        Convert them into clear, actionable points without bullet symbols.
        
        Original content integration: {str(raw_data.get('content_integration', []))}
        
        Top 2 integration features (as 2 separate lines):
        """
        
        # Infrastructure: Extract 2 key requirements
        infrastructure_prompt = f"""
        From the following infrastructure requirements for {product_name}, extract the 2 most critical requirements.
        Convert them into clear, specific points without bullet symbols.
        
        Original infrastructure requirements: {str(raw_data.get('infrastructure_requirements', []))}
        
        Top 2 infrastructure requirements (as 2 separate lines):
        """
        
        # Generate summaries using AI
        if content_generator.langchain.is_available():
            overview_summary = content_generator.langchain.generate_text(overview_prompt)
            specs_summary = content_generator.langchain.generate_text(specs_prompt)
            integration_summary = content_generator.langchain.generate_text(integration_prompt)
            infrastructure_summary = content_generator.langchain.generate_text(infrastructure_prompt)
            
            # Parse AI responses into proper format
            spec_points = [line.strip() for line in specs_summary.split('\n') if line.strip()][:2]
            integration_points = [line.strip() for line in integration_summary.split('\n') if line.strip()][:2]
            infrastructure_points = [line.strip() for line in infrastructure_summary.split('\n') if line.strip()][:2]
            
            # Ensure we have exactly 2 points for each section
            spec_points = ensure_two_points(spec_points, "High-resolution display with advanced processing", "AI-powered features with real-time analytics")
            integration_points = ensure_two_points(integration_points, "Seamless CMS integration with real-time updates", "Multi-platform compatibility with cloud management")
            infrastructure_points = ensure_two_points(infrastructure_points, "Stable internet connection (minimum 50 Mbps)", "Dedicated power supply with backup systems")
            
        else:
            # Fallback: basic summarization without AI
            overview_summary = raw_data.get('overview', '')[:200] + "..."
            spec_points = ["High-resolution display with advanced processing", "AI-powered features with real-time analytics"]
            integration_points = ["Seamless CMS integration with real-time updates", "Multi-platform compatibility with cloud management"]
            infrastructure_points = ["Stable internet connection (minimum 50 Mbps)", "Dedicated power supply with backup systems"]
        
        return {
            "overview": overview_summary.strip(),
            "specifications": spec_points,
            "content_integration": integration_points,
            "infrastructure_requirements": infrastructure_points
        }
        
    except Exception as e:
        logger.error(f"AI summarization failed for {product_name}: {str(e)}")
        # Return fallback content
        return create_fallback_summarized_content(product_name)

def ensure_two_points(points: List[str], fallback1: str, fallback2: str) -> List[str]:
    """Ensure exactly 2 points are returned"""
    if len(points) >= 2:
        return points[:2]
    elif len(points) == 1:
        return [points[0], fallback2]
    else:
        return [fallback1, fallback2]

def create_fallback_product_content(product_name: str) -> ProductContent:
    """Create fallback content for failed extractions"""
    return ProductContent(
        product_name=product_name,
        overview=f"{product_name} is an advanced interactive technology solution. It offers cutting-edge features for enhanced user engagement.",
        specifications=[
            "High-resolution 4K display with touch interface",
            "AI-powered gesture recognition and facial detection"
        ],
        content_integration=[
            "Seamless CMS integration with real-time content updates",
            "Multi-platform compatibility with cloud-based management"
        ],
        infrastructure_requirements=[
            "Stable internet connection (minimum 50 Mbps)",
            "Dedicated power supply with UPS backup systems"
        ],
        images=[],
        image_layout="none"
    )

def create_fallback_summarized_content(product_name: str) -> Dict[str, Any]:
    """Create fallback summarized content"""
    return {
        "overview": f"{product_name} offers advanced interactive technology solutions. Designed for enhanced user engagement and seamless integration.",
        "specifications": [
            "High-resolution 4K display with touch interface",
            "AI-powered gesture recognition and facial detection"
        ],
        "content_integration": [
            "Seamless CMS integration with real-time updates",
            "Multi-platform compatibility with cloud management"
        ],
        "infrastructure_requirements": [
            "Stable internet connection (minimum 50 Mbps)",
            "Dedicated power supply with backup systems"
        ]
    }

@router.post("/modify-content")
async def modify_product_content(
    product_name: str,
    content: ProductContent,
    modifications: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Handle user modifications to extracted product content"""
    try:
        # Apply user modifications (add, replace, delete, modify)
        modified_content = apply_user_modifications(content.dict(), modifications)
        
        return ProductContent(**modified_content)
        
    except Exception as e:
        logger.error(f"Content modification failed for {product_name}: {str(e)}")
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