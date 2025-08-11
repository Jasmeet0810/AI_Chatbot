import requests
from PIL import Image
import io
import os
from typing import List, Optional
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.max_file_size = settings.max_file_size
        
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def download_and_convert_image(self, image_url: str, output_filename: str) -> Optional[str]:
        """Download and convert WebP images to PNG/JPG"""
        try:
            logger.info(f"Downloading image: {image_url}")
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_file_size:
                logger.warning(f"Image too large: {content_length} bytes")
                return None
            
            # Open image with Pillow
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize if too large
            max_size = (1920, 1080)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to: {image.size}")
            
            # Determine output format and path
            output_path = os.path.join(self.upload_dir, output_filename)
            
            # Convert WebP and other formats to PNG for better PPT compatibility
            if image.format in ['WEBP', 'GIF', 'BMP', 'TIFF']:
                if not output_path.lower().endswith('.png'):
                    output_path = os.path.splitext(output_path)[0] + '.png'
                image.save(output_path, 'PNG', optimize=True)
                logger.info(f"Converted {image.format} to PNG: {output_path}")
            else:
                # Keep as JPEG for photos
                if not output_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    output_path = os.path.splitext(output_path)[0] + '.jpg'
                
                if output_path.lower().endswith('.png'):
                    image.save(output_path, 'PNG', optimize=True)
                else:
                    image.save(output_path, 'JPEG', quality=85, optimize=True)
                
                logger.info(f"Saved image as: {output_path}")
            
            return output_path
            
        except requests.RequestException as e:
            logger.error(f"Failed to download image {image_url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to process image {image_url}: {str(e)}")
            return None
    
    def process_images(self, image_urls: List[str], prefix: str = "img") -> List[str]:
        """Process multiple images and return local file paths"""
        processed_images = []
        
        for i, url in enumerate(image_urls):
            try:
                # Generate unique filename
                filename = f"{prefix}_{i+1}_{hash(url) % 10000}.png"
                
                # Process image
                local_path = self.download_and_convert_image(url, filename)
                if local_path:
                    processed_images.append(local_path)
                    logger.info(f"Successfully processed image {i+1}/{len(image_urls)}")
                else:
                    logger.warning(f"Failed to process image {i+1}/{len(image_urls)}: {url}")
                    
            except Exception as e:
                logger.error(f"Error processing image {url}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(processed_images)}/{len(image_urls)} images")
        return processed_images
    
    def cleanup_images(self, image_paths: List[str]):
        """Clean up temporary image files"""
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"Cleaned up image: {path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup image {path}: {str(e)}")
    
    def get_image_info(self, image_path: str) -> dict:
        """Get image information"""
        try:
            with Image.open(image_path) as img:
                return {
                    "size": img.size,
                    "format": img.format,
                    "mode": img.mode,
                    "file_size": os.path.getsize(image_path)
                }
        except Exception as e:
            logger.error(f"Failed to get image info for {image_path}: {str(e)}")
            return {}