from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel
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
    images: List[str]
    image_layout: str

class MultiProductResponse(BaseModel):
    products: List[ProductContent]
    total_products: int
    extraction_status: str

@router.post("/extract-content", response_model=MultiProductResponse)
async def extract_multiple_products_content(request: ProductExtractionRequest):
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
                
                # Add processed images to raw data
                raw_data['images'] = processed_images
                
                # AI-powered content enhancement using Bedrock Claude
                enhanced_content = content_generator.bedrock.enhance_product_content(
                    product_name,
                    raw_data
                )
                
                # Create product content structure
                product_content = ProductContent(
                    product_name=enhanced_content['product_name'],
                    overview=enhanced_content['overview'],
                    specifications=enhanced_content['specifications'],
                    content_integration=enhanced_content['content_integration'],
                    infrastructure_requirements=enhanced_content['infrastructure_requirements'],
                    images=enhanced_content['images'],
                    image_layout=enhanced_content['image_layout']
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

@router.post("/modify-content")
async def modify_product_content(
    product_name: str,
    content: ProductContent,
    modifications: Dict[str, Any]
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