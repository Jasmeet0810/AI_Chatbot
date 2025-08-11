from typing import Dict, List, Any
import re
import logging
from .lazulite_scraper import LazuliteScraper
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self):
        self.scraper = LazuliteScraper()
        self.image_processor = ImageProcessor()
    
    def extract_complete_product_data(self, product_url: str = None) -> Dict[str, Any]:
        """Extract complete product data including processed images"""
        try:
            logger.info("Starting complete product data extraction")
            
            # Scrape raw data
            raw_data = self.scraper.scrape_product_data(product_url)
            
            # Process images
            processed_images = []
            if raw_data.get('images'):
                logger.info(f"Processing {len(raw_data['images'])} images")
                processed_images = self.image_processor.process_images(
                    raw_data['images'], 
                    prefix=self.sanitize_filename(raw_data['name'])
                )
            
            # Clean and structure the data
            structured_data = {
                "name": self.clean_text(raw_data.get('name', 'Lazulite Product')),
                "overview": self.clean_text(raw_data.get('overview', '')),
                "specifications": self.clean_specifications(raw_data.get('specifications', {})),
                "content_integration": self.clean_list_items(raw_data.get('content_integration', [])),
                "infrastructure_requirements": self.clean_list_items(raw_data.get('infrastructure_requirements', [])),
                "images": {
                    "original_urls": raw_data.get('images', []),
                    "processed_paths": processed_images,
                    "count": len(processed_images)
                },
                "metadata": {
                    "source_url": product_url or self.scraper.base_url,
                    "extraction_timestamp": self.get_timestamp(),
                    "total_sections": self.count_data_sections(raw_data)
                }
            }
            
            logger.info("Successfully extracted and processed complete product data")
            return structured_data
            
        except Exception as e:
            logger.error(f"Failed to extract complete product data: {str(e)}")
            raise Exception(f"Data extraction failed: {str(e)}")
        finally:
            # Clean up scraper
            self.scraper.close()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?():]', '', text)
        
        return text
    
    def clean_specifications(self, specs: Dict[str, str]) -> Dict[str, str]:
        """Clean and normalize specifications"""
        cleaned_specs = {}
        
        for key, value in specs.items():
            if key and value:
                # Clean key
                clean_key = self.clean_text(key)
                clean_key = clean_key.title()  # Capitalize first letters
                
                # Clean value
                clean_value = self.clean_text(value)
                
                if clean_key and clean_value:
                    cleaned_specs[clean_key] = clean_value
        
        return cleaned_specs
    
    def clean_list_items(self, items: List[str]) -> List[str]:
        """Clean and normalize list items"""
        cleaned_items = []
        
        for item in items:
            if item:
                clean_item = self.clean_text(item)
                if clean_item and len(clean_item) > 5:  # Filter out very short items
                    cleaned_items.append(clean_item)
        
        return cleaned_items
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations"""
        if not filename:
            return "product"
        
        # Remove or replace invalid characters
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        
        return filename.lower()[:50]  # Limit length
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def count_data_sections(self, data: Dict) -> int:
        """Count non-empty data sections"""
        count = 0
        sections = ['name', 'overview', 'specifications', 'content_integration', 'infrastructure_requirements', 'images']
        
        for section in sections:
            if data.get(section):
                if isinstance(data[section], (list, dict)):
                    if len(data[section]) > 0:
                        count += 1
                elif isinstance(data[section], str):
                    if len(data[section].strip()) > 0:
                        count += 1
        
        return count
    
    def validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure minimum data quality"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check required fields
        if not data.get('name') or len(data['name']) < 3:
            validation_result["errors"].append("Product name is missing or too short")
            validation_result["is_valid"] = False
        
        if not data.get('overview') or len(data['overview']) < 50:
            validation_result["warnings"].append("Product overview is missing or too short")
        
        if not data.get('specifications') or len(data['specifications']) == 0:
            validation_result["warnings"].append("No specifications found")
        
        if not data.get('images', {}).get('processed_paths'):
            validation_result["warnings"].append("No images were successfully processed")
        
        # Check data quality
        total_content_length = len(data.get('overview', ''))
        total_content_length += sum(len(str(v)) for v in data.get('specifications', {}).values())
        total_content_length += sum(len(item) for item in data.get('content_integration', []))
        
        if total_content_length < 200:
            validation_result["warnings"].append("Very little content extracted - data quality may be low")
        
        return validation_result
    
    def cleanup_processed_files(self, data: Dict[str, Any]):
        """Clean up processed image files"""
        try:
            processed_paths = data.get('images', {}).get('processed_paths', [])
            if processed_paths:
                self.image_processor.cleanup_images(processed_paths)
                logger.info(f"Cleaned up {len(processed_paths)} processed image files")
        except Exception as e:
            logger.warning(f"Failed to cleanup processed files: {str(e)}")