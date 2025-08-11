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
import logging

logger = logging.getLogger(__name__)

class LazuliteScraper:
    def __init__(self):
        self.base_url = settings.lazulite_base_url
        self.timeout = settings.selenium_timeout
        self.max_images = settings.max_images_per_product
        self.driver = None
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
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise Exception(f"WebDriver initialization failed: {str(e)}")
    
    def scrape_product_data(self, product_url: str = None) -> Dict:
        """Scrape product data from Lazulite website"""
        if not product_url:
            product_url = self.base_url
            
        try:
            logger.info(f"Scraping product data from: {product_url}")
            self.driver.get(product_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract product data based on the structure
            product_data = {
                "name": self.extract_product_name(soup),
                "overview": self.extract_overview(soup),
                "images": self.extract_images(soup, product_url),
                "specifications": self.extract_specifications(soup),
                "content_integration": self.extract_content_integration(soup),
                "infrastructure_requirements": self.extract_infrastructure(soup)
            }
            
            logger.info(f"Successfully scraped product data: {product_data['name']}")
            return product_data
            
        except Exception as e:
            logger.error(f"Failed to scrape product data: {str(e)}")
            raise Exception(f"Failed to scrape product data: {str(e)}")
    
    def extract_product_name(self, soup) -> str:
        """Extract product name"""
        try:
            # Try multiple selectors for product name
            selectors = [
                'h1.product-title',
                'h1.page-title',
                '.product-name h1',
                'h1',
                'title'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text().strip()
                    if name and len(name) > 3:
                        return name
            
            return "Lazulite Product"
        except Exception as e:
            logger.warning(f"Failed to extract product name: {str(e)}")
            return "Lazulite Product"
    
    def extract_overview(self, soup) -> str:
        """Extract product overview"""
        try:
            # Try multiple selectors for overview
            selectors = [
                '.product-overview',
                '.product-description',
                '.overview-section',
                '.description',
                '.intro-text'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    overview = element.get_text().strip()
                    if overview and len(overview) > 50:
                        return overview
            
            # Fallback: get first few paragraphs
            paragraphs = soup.find_all('p')
            overview_text = ""
            for p in paragraphs[:3]:
                text = p.get_text().strip()
                if text and len(text) > 20:
                    overview_text += text + " "
            
            return overview_text.strip() if overview_text else "Product overview not available"
            
        except Exception as e:
            logger.warning(f"Failed to extract overview: {str(e)}")
            return "Product overview not available"
    
    def extract_images(self, soup, base_url: str) -> List[str]:
        """Extract and process product images"""
        try:
            images = []
            img_elements = soup.find_all('img')
            
            for img in img_elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and self.is_product_image(src):
                    # Convert relative URLs to absolute
                    if src.startswith('/'):
                        src = f"https://lazulite.ae{src}"
                    elif src.startswith('./'):
                        src = f"{base_url.rstrip('/')}/{src[2:]}"
                    elif not src.startswith('http'):
                        src = f"{base_url.rstrip('/')}/{src}"
                    
                    images.append(src)
                    
                    if len(images) >= self.max_images:
                        break
            
            logger.info(f"Extracted {len(images)} product images")
            return images
            
        except Exception as e:
            logger.warning(f"Failed to extract images: {str(e)}")
            return []
    
    def extract_specifications(self, soup) -> Dict[str, str]:
        """Extract key specifications"""
        try:
            specs = {}
            
            # Try multiple selectors for specifications
            spec_selectors = [
                '.specifications',
                '.specs',
                '.product-specs',
                '.features',
                '.technical-specs'
            ]
            
            for selector in spec_selectors:
                spec_section = soup.select_one(selector)
                if spec_section:
                    # Extract specification items
                    spec_items = spec_section.find_all(['li', 'div', 'p', 'tr'])
                    for item in spec_items:
                        text = item.get_text().strip()
                        if ':' in text:
                            parts = text.split(':', 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                if key and value:
                                    specs[key] = value
                    
                    if specs:
                        break
            
            # Fallback: look for common specification patterns
            if not specs:
                all_text = soup.get_text()
                lines = all_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if ':' in line and len(line) < 200:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value and len(key) < 50:
                                specs[key] = value
            
            logger.info(f"Extracted {len(specs)} specifications")
            return specs
            
        except Exception as e:
            logger.warning(f"Failed to extract specifications: {str(e)}")
            return {}
    
    def extract_content_integration(self, soup) -> List[str]:
        """Extract content integration information"""
        try:
            integration_items = []
            
            # Try multiple selectors
            selectors = [
                '.content-integration',
                '.integration',
                '.connectivity',
                '.features'
            ]
            
            for selector in selectors:
                section = soup.select_one(selector)
                if section:
                    items = section.find_all(['li', 'p', 'div'])
                    for item in items:
                        text = item.get_text().strip()
                        if text and len(text) > 10 and len(text) < 200:
                            integration_items.append(text)
                    
                    if integration_items:
                        break
            
            logger.info(f"Extracted {len(integration_items)} content integration items")
            return integration_items[:10]  # Limit to 10 items
            
        except Exception as e:
            logger.warning(f"Failed to extract content integration: {str(e)}")
            return []
    
    def extract_infrastructure(self, soup) -> List[str]:
        """Extract infrastructure requirements"""
        try:
            requirements = []
            
            # Try multiple selectors
            selectors = [
                '.infrastructure',
                '.requirements',
                '.system-requirements',
                '.technical-requirements'
            ]
            
            for selector in selectors:
                section = soup.select_one(selector)
                if section:
                    items = section.find_all(['li', 'p', 'div'])
                    for item in items:
                        text = item.get_text().strip()
                        if text and len(text) > 10 and len(text) < 200:
                            requirements.append(text)
                    
                    if requirements:
                        break
            
            logger.info(f"Extracted {len(requirements)} infrastructure requirements")
            return requirements[:10]  # Limit to 10 items
            
        except Exception as e:
            logger.warning(f"Failed to extract infrastructure requirements: {str(e)}")
            return []
    
    def is_product_image(self, src: str) -> bool:
        """Check if image is a product image"""
        if not src:
            return False
            
        # Filter out logos, icons, etc.
        exclude_keywords = [
            'logo', 'icon', 'favicon', 'banner', 'header', 'footer',
            'social', 'arrow', 'button', 'bg', 'background'
        ]
        
        src_lower = src.lower()
        return not any(keyword in src_lower for keyword in exclude_keywords)
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()