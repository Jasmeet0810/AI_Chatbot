import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
import os
from typing import Dict, List, Optional
from ..config import settings
from .image_processor import ImageProcessor
import logging
import re

logger = logging.getLogger(__name__)

class MultiProductExtractor:
    def __init__(self):
        self.base_url = "https://lazulite.ae/activations"
        self.timeout = settings.selenium_timeout
        self.max_images = settings.max_images_per_product
        self.driver = None
        self.image_processor = ImageProcessor()
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Selenium WebDriver for dynamic content"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            logger.info("Chrome WebDriver initialized for multi-product extraction")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise Exception(f"WebDriver initialization failed: {str(e)}")
    
    def extract_single_product_data(self, product_name: str, base_url: str = None) -> Dict:
        """Extract data for a single product from Lazulite website"""
        if not base_url:
            base_url = self.base_url
            
        try:
            logger.info(f"Extracting data for product: {product_name}")
            
            # Navigate to the activations page
            self.driver.get(base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find product-specific content
            product_data = self.find_product_content(product_name)
            
            logger.info(f"Successfully extracted data for: {product_name}")
            return product_data
            
        except Exception as e:
            logger.error(f"Failed to extract data for {product_name}: {str(e)}")
            raise Exception(f"Failed to extract data for {product_name}: {str(e)}")
    
    def find_product_content(self, product_name: str) -> Dict:
        """Find and extract content specific to the product"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Search for product-specific sections
            product_section = self.locate_product_section(soup, product_name)
            
            if not product_section:
                # Fallback: extract general content and filter
                logger.warning(f"Specific section not found for {product_name}, using general extraction")
                return self.extract_general_content(soup, product_name)
            
            # Extract content from the specific product section
            return self.extract_product_section_content(product_section, product_name)
            
        except Exception as e:
            logger.error(f"Failed to find product content for {product_name}: {str(e)}")
            return self.create_fallback_data(product_name)
    
    def locate_product_section(self, soup, product_name: str):
        """Locate the specific section for the product"""
        try:
            # Clean product name for searching
            clean_name = self.clean_product_name(product_name)
            
            # Search strategies
            search_patterns = [
                clean_name.lower(),
                clean_name.replace(' ', '-').lower(),
                clean_name.replace(' ', '_').lower(),
                clean_name.replace(' ', '').lower()
            ]
            
            # Look for product-specific containers
            for pattern in search_patterns:
                # Try different selectors
                selectors = [
                    f'[id*="{pattern}"]',
                    f'[class*="{pattern}"]',
                    f'[data-product*="{pattern}"]',
                    f'h1:contains("{product_name}")',
                    f'h2:contains("{product_name}")',
                    f'h3:contains("{product_name}")'
                ]
                
                for selector in selectors:
                    try:
                        elements = soup.select(selector)
                        if elements:
                            # Find the parent container
                            for element in elements:
                                parent = element.find_parent(['div', 'section', 'article'])
                                if parent and len(parent.get_text().strip()) > 100:
                                    return parent
                    except Exception:
                        continue
            
            # Text-based search
            all_text_elements = soup.find_all(text=re.compile(product_name, re.IGNORECASE))
            for text_element in all_text_elements:
                parent = text_element.find_parent(['div', 'section', 'article'])
                if parent and len(parent.get_text().strip()) > 200:
                    return parent
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to locate product section for {product_name}: {str(e)}")
            return None
    
    def extract_product_section_content(self, section, product_name: str) -> Dict:
        """Extract content from a specific product section"""
        try:
            return {
                "name": product_name,
                "overview": self.extract_overview_from_section(section),
                "images": self.extract_images_from_section(section),
                "specifications": self.extract_specifications_from_section(section),
                "content_integration": self.extract_content_integration_from_section(section),
                "infrastructure_requirements": self.extract_infrastructure_from_section(section)
            }
        except Exception as e:
            logger.error(f"Failed to extract content from section for {product_name}: {str(e)}")
            return self.create_fallback_data(product_name)
    
    def extract_general_content(self, soup, product_name: str) -> Dict:
        """Extract general content and filter for product relevance"""
        try:
            # Get all content and filter for product-relevant information
            all_paragraphs = soup.find_all('p')
            all_lists = soup.find_all(['ul', 'ol'])
            all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            
            # Filter content that mentions the product
            relevant_content = []
            product_keywords = self.generate_product_keywords(product_name)
            
            for element in all_paragraphs + all_lists + all_headings:
                text = element.get_text().lower()
                if any(keyword in text for keyword in product_keywords):
                    relevant_content.append(element)
            
            return {
                "name": product_name,
                "overview": self.extract_overview_from_elements(relevant_content),
                "images": self.extract_images_from_soup(soup),
                "specifications": self.extract_specifications_from_elements(relevant_content),
                "content_integration": self.extract_content_integration_from_elements(relevant_content),
                "infrastructure_requirements": self.extract_infrastructure_from_elements(relevant_content)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract general content for {product_name}: {str(e)}")
            return self.create_fallback_data(product_name)
    
    def extract_overview_from_section(self, section) -> str:
        """Extract overview from product section"""
        try:
            # Look for overview-like content
            overview_selectors = [
                '.overview', '.description', '.intro', '.summary',
                'p:first-of-type', '.product-description'
            ]
            
            for selector in overview_selectors:
                element = section.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    if len(text) > 50:
                        return text
            
            # Fallback: get first substantial paragraph
            paragraphs = section.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 50:
                    return text
            
            return "Product overview not available"
            
        except Exception as e:
            logger.warning(f"Failed to extract overview from section: {str(e)}")
            return "Product overview not available"
    
    def extract_images_from_section(self, section) -> List[str]:
        """Extract images from product section"""
        try:
            images = []
            img_elements = section.find_all('img')
            
            for img in img_elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and self.is_product_image(src):
                    # Convert to absolute URL
                    if src.startswith('/'):
                        src = f"https://lazulite.ae{src}"
                    elif not src.startswith('http'):
                        src = f"https://lazulite.ae/{src.lstrip('./')}"
                    
                    images.append(src)
                    
                    if len(images) >= self.max_images:
                        break
            
            return images
            
        except Exception as e:
            logger.warning(f"Failed to extract images from section: {str(e)}")
            return []
    
    def extract_specifications_from_section(self, section) -> Dict[str, str]:
        """Extract specifications from product section"""
        try:
            specs = {}
            
            # Look for specification lists
            spec_lists = section.find_all(['ul', 'ol'])
            for spec_list in spec_lists:
                items = spec_list.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if ':' in text:
                        parts = text.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value:
                                specs[key] = value
            
            # Look for specification tables
            tables = section.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text().strip()
                        value = cells[1].get_text().strip()
                        if key and value:
                            specs[key] = value
            
            return specs
            
        except Exception as e:
            logger.warning(f"Failed to extract specifications from section: {str(e)}")
            return {}
    
    def extract_content_integration_from_section(self, section) -> List[str]:
        """Extract content integration info from section"""
        try:
            integration_items = []
            
            # Look for integration-related content
            integration_keywords = ['integration', 'cms', 'content', 'management', 'api', 'connectivity']
            
            all_text_elements = section.find_all(['p', 'li', 'div'])
            for element in all_text_elements:
                text = element.get_text().strip()
                if any(keyword in text.lower() for keyword in integration_keywords):
                    if len(text) > 20 and len(text) < 300:
                        integration_items.append(text)
            
            return integration_items[:10]
            
        except Exception as e:
            logger.warning(f"Failed to extract content integration from section: {str(e)}")
            return []
    
    def extract_infrastructure_from_section(self, section) -> List[str]:
        """Extract infrastructure requirements from section"""
        try:
            requirements = []
            
            # Look for requirement-related content
            requirement_keywords = ['requirement', 'installation', 'setup', 'power', 'network', 'system']
            
            all_text_elements = section.find_all(['p', 'li', 'div'])
            for element in all_text_elements:
                text = element.get_text().strip()
                if any(keyword in text.lower() for keyword in requirement_keywords):
                    if len(text) > 20 and len(text) < 300:
                        requirements.append(text)
            
            return requirements[:10]
            
        except Exception as e:
            logger.warning(f"Failed to extract infrastructure from section: {str(e)}")
            return []
    
    def process_product_images(self, image_urls: List[str], product_name: str) -> List[str]:
        """Process and convert product images"""
        try:
            if not image_urls:
                return []
            
            logger.info(f"Processing {len(image_urls)} images for {product_name}")
            
            # Use image processor to convert WebP to PNG/JPG
            processed_paths = self.image_processor.process_images(
                image_urls, 
                prefix=self.clean_product_name(product_name)
            )
            
            logger.info(f"Successfully processed {len(processed_paths)} images for {product_name}")
            return processed_paths
            
        except Exception as e:
            logger.error(f"Failed to process images for {product_name}: {str(e)}")
            return []
    
    def clean_product_name(self, product_name: str) -> str:
        """Clean product name for file operations"""
        # Remove special characters and spaces
        clean_name = re.sub(r'[^\w\s-]', '', product_name)
        clean_name = re.sub(r'[-\s]+', '_', clean_name)
        return clean_name.lower()
    
    def generate_product_keywords(self, product_name: str) -> List[str]:
        """Generate keywords for product content filtering"""
        keywords = [product_name.lower()]
        
        # Add variations
        words = product_name.lower().split()
        keywords.extend(words)
        
        # Add common variations
        keywords.append(product_name.replace(' ', '').lower())
        keywords.append(product_name.replace(' ', '-').lower())
        
        return keywords
    
    def is_product_image(self, src: str) -> bool:
        """Check if image is a product image"""
        if not src:
            return False
            
        # Filter out logos, icons, etc.
        exclude_keywords = [
            'logo', 'icon', 'favicon', 'banner', 'header', 'footer',
            'social', 'arrow', 'button', 'bg', 'background', 'nav'
        ]
        
        src_lower = src.lower()
        return not any(keyword in src_lower for keyword in exclude_keywords)
    
    def create_fallback_data(self, product_name: str) -> Dict:
        """Create fallback data when extraction fails"""
        return {
            "name": product_name,
            "overview": f"{product_name} is an advanced interactive technology solution from Lazulite.",
            "images": [],
            "specifications": {
                "Display": "High-resolution display",
                "Technology": "Advanced interactive technology"
            },
            "content_integration": [
                "Content management system integration",
                "Real-time content updates"
            ],
            "infrastructure_requirements": [
                "Stable internet connection required",
                "Dedicated power supply needed"
            ]
        }
    
    def extract_overview_from_elements(self, elements) -> str:
        """Extract overview from filtered elements"""
        for element in elements:
            text = element.get_text().strip()
            if len(text) > 50 and len(text) < 500:
                return text
        return "Product overview not available"
    
    def extract_images_from_soup(self, soup) -> List[str]:
        """Extract images from entire soup"""
        images = []
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src and self.is_product_image(src):
                if src.startswith('/'):
                    src = f"https://lazulite.ae{src}"
                images.append(src)
                
                if len(images) >= self.max_images:
                    break
        
        return images
    
    def extract_specifications_from_elements(self, elements) -> Dict[str, str]:
        """Extract specifications from filtered elements"""
        specs = {}
        for element in elements:
            text = element.get_text()
            if ':' in text:
                lines = text.split('\n')
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value and len(key) < 50:
                                specs[key] = value
        return specs
    
    def extract_content_integration_from_elements(self, elements) -> List[str]:
        """Extract content integration from filtered elements"""
        integration_items = []
        integration_keywords = ['integration', 'cms', 'content', 'api']
        
        for element in elements:
            text = element.get_text().strip()
            if any(keyword in text.lower() for keyword in integration_keywords):
                if len(text) > 20 and len(text) < 200:
                    integration_items.append(text)
        
        return integration_items[:5]
    
    def extract_infrastructure_from_elements(self, elements) -> List[str]:
        """Extract infrastructure requirements from filtered elements"""
        requirements = []
        requirement_keywords = ['requirement', 'power', 'network', 'installation']
        
        for element in elements:
            text = element.get_text().strip()
            if any(keyword in text.lower() for keyword in requirement_keywords):
                if len(text) > 20 and len(text) < 200:
                    requirements.append(text)
        
        return requirements[:5]
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("Multi-product extractor WebDriver closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()