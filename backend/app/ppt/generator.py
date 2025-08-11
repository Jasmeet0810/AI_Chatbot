from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os
from typing import Dict, List, Optional
from ..ai.content_generator import ContentGenerator
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class PPTGenerator:
    def __init__(self, template_path: Optional[str] = None):
        self.template_path = template_path or os.path.join(settings.template_dir, "lazulite_template.pptx")
        self.content_generator = ContentGenerator()
        self.output_dir = settings.generated_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_presentation(self, product_data: Dict, user_prompt: str, user_id: str = None) -> str:
        """Generate PPT from product data and user prompt"""
        try:
            logger.info(f"Starting PPT generation for prompt: {user_prompt[:50]}...")
            
            # Load template or create new presentation
            if os.path.exists(self.template_path):
                prs = Presentation(self.template_path)
                logger.info(f"Loaded template: {self.template_path}")
            else:
                prs = Presentation()
                logger.info("Created new presentation (template not found)")
            
            # Generate AI-enhanced content
            enhanced_content = self.content_generator.enhance_content(product_data, user_prompt)
            
            # Clear existing slides if using template
            if len(prs.slides) > 0:
                # Keep the first slide as title slide
                slides_to_remove = list(prs.slides)[1:]
                for slide in slides_to_remove:
                    rId = prs.slides._sldIdLst[prs.slides.index(slide)].rId
                    prs.part.drop_rel(rId)
                    del prs.slides._sldIdLst[prs.slides.index(slide)]
            
            # Create slides
            self.create_title_slide(prs, enhanced_content)
            self.create_overview_slide(prs, enhanced_content)
            self.create_specifications_slide(prs, enhanced_content)
            self.create_content_integration_slide(prs, enhanced_content)
            self.create_infrastructure_slide(prs, enhanced_content)
            self.create_conclusion_slide(prs, enhanced_content)
            
            # Generate unique filename
            safe_prompt = self._sanitize_filename(user_prompt)
            filename = f"presentation_{user_id or 'user'}_{safe_prompt}_{hash(user_prompt) % 10000}.pptx"
            output_path = os.path.join(self.output_dir, filename)
            
            # Save presentation
            prs.save(output_path)
            logger.info(f"PPT saved successfully: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate presentation: {str(e)}")
            raise Exception(f"Failed to generate presentation: {str(e)}")
    
    def create_title_slide(self, prs, content):
        """Create title slide"""
        if len(prs.slides) == 0:
            slide_layout = prs.slide_layouts[0]  # Title slide layout
            slide = prs.slides.add_slide(slide_layout)
        else:
            slide = prs.slides[0]
        
        # Update title and subtitle
        if slide.shapes.title:
            slide.shapes.title.text = content.get('title', 'Lazulite Product Presentation')
        
        # Find subtitle placeholder
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 1:  # Subtitle placeholder
                shape.text = content.get('subtitle', 'Powered by Lazulite AI Technology')
                break
    
    def create_overview_slide(self, prs, content):
        """Create product overview slide with images"""
        slide_layout = prs.slide_layouts[1]  # Content with caption layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        slide.shapes.title.text = "Product Overview"
        
        # Add content
        if len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            content_placeholder.text = content.get('overview_text', 'Product overview not available')
        
        # Add images if available
        images = content.get('images', [])
        if images:
            self.add_images_to_slide(slide, images[:4])  # Max 4 images
    
    def create_specifications_slide(self, prs, content):
        """Create specifications slide"""
        slide_layout = prs.slide_layouts[1]  # Content layout
        slide = prs.slides.add_slide(slide_layout)
        
        slide.shapes.title.text = "Key Specifications"
        
        # Add specifications content
        specs_text = content.get('specifications_text', 'Specifications not available')
        if len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            content_placeholder.text = specs_text
    
    def create_content_integration_slide(self, prs, content):
        """Create content integration slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        slide.shapes.title.text = "Content Integration"
        
        integration_text = content.get('integration_text', 'Content integration information not available')
        if len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            content_placeholder.text = integration_text
    
    def create_infrastructure_slide(self, prs, content):
        """Create infrastructure requirements slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        slide.shapes.title.text = "Infrastructure Requirements"
        
        infrastructure_text = content.get('infrastructure_text', 'Infrastructure requirements not available')
        if len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            content_placeholder.text = infrastructure_text
    
    def create_conclusion_slide(self, prs, content):
        """Create conclusion slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        slide.shapes.title.text = "Thank You"
        
        conclusion_text = "Thank you for your interest in Lazulite products!\n\nFor more information, visit: https://lazulite.ae"
        if len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            content_placeholder.text = conclusion_text
    
    def add_images_to_slide(self, slide, images: List[str]):
        """Add converted images to slide"""
        try:
            # Position images in a grid
            img_width = Inches(2.5)
            img_height = Inches(1.8)
            
            for i, img_path in enumerate(images):
                if os.path.exists(img_path):
                    # Calculate position (2x2 grid)
                    col = i % 2
                    row = i // 2
                    left = Inches(0.5 + col * 3)
                    top = Inches(3 + row * 2.2)
                    
                    try:
                        slide.shapes.add_picture(img_path, left, top, img_width, img_height)
                        logger.info(f"Added image to slide: {img_path}")
                    except Exception as e:
                        logger.warning(f"Failed to add image {img_path}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Failed to add images to slide: {str(e)}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations"""
        import re
        if not filename:
            return "presentation"
        
        # Remove or replace invalid characters
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        
        return filename.lower()[:30]  # Limit length
    
    def get_presentation_info(self, file_path: str) -> Dict:
        """Get information about generated presentation"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            prs = Presentation(file_path)
            return {
                "slide_count": len(prs.slides),
                "file_size": os.path.getsize(file_path),
                "file_path": file_path,
                "filename": os.path.basename(file_path)
            }
        except Exception as e:
            logger.error(f"Failed to get presentation info: {str(e)}")
            return {"error": str(e)}