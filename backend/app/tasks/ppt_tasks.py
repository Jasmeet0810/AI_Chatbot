from celery import current_task
from .celery_app import celery_app
from ..scraping.data_extractor import DataExtractor
from ..ppt.generator import PPTGenerator
from ..ppt.templates import PPTTemplateManager
from ..database import SessionLocal, PPTGeneration
from ..config import settings
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def generate_ppt_task(self, generation_id: str, user_id: str, prompt: str, product_url: str, template: Optional[str] = None):
    """Background task for PPT generation"""
    db = SessionLocal()
    
    try:
        logger.info(f"Starting PPT generation task for user {user_id}")
        
        # Update task progress
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 'Initializing PPT generation...', 'step': 1, 'total_steps': 6}
        )
        
        # Get generation record
        generation = db.query(PPTGeneration).filter(PPTGeneration.id == generation_id).first()
        if not generation:
            raise Exception("Generation record not found")
        
        generation.status = "processing"
        db.commit()
        
        # Step 1: Initialize components
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 'Extracting product data from Lazulite website...', 'step': 2, 'total_steps': 6}
        )
        
        from ..scraping.multi_product_extractor import MultiProductExtractor
        multi_extractor = MultiProductExtractor()
        
        # Step 2: Extract product data
        try:
            # Parse product names from prompt (simplified)
            import re
            product_match = re.search(r'products?:\s*([^.]+)', prompt, re.IGNORECASE)
            if product_match:
                product_names = [name.strip() for name in product_match.group(1).split(',')]
            else:
                product_names = ['AI Photobooth']  # Default fallback
            
            # Extract data for each product
            multi_product_data = []
            for product_name in product_names:
                product_data = multi_extractor.extract_single_product_data(product_name, product_url)
                
                # Process images
                processed_images = multi_extractor.process_product_images(
                    product_data.get('images', []),
                    product_name
                )
                
                # Add processed data
                product_data['images'] = processed_images
                product_data['image_layout'] = 'single' if len(processed_images) == 1 else 'side_by_side' if len(processed_images) == 2 else 'grid'
                multi_product_data.append(product_data)
            
            logger.info(f"Extracted data for {len(multi_product_data)} products")
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            raise Exception(f"Failed to extract product data: {str(e)}")
        
        # Step 3: Validate extracted data
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 'Validating extracted data...', 'step': 3, 'total_steps': 6}
        )
        
        # Validate each product's data
        for product_data in multi_product_data:
            if not product_data.get('name'):
                logger.warning(f"Product missing name: {product_data}")
        
        # Step 4: Prepare template
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 'Preparing presentation template...', 'step': 4, 'total_steps': 6}
        )
        
        template_manager = PPTTemplateManager()
        template_path = template_manager.ensure_template_exists()
        
        # Step 5: Generate PPT
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 'Generating PowerPoint presentation...', 'step': 5, 'total_steps': 6}
        )
        
        generator = PPTGenerator(template_path)
        
        try:
            ppt_path = generator.generate_presentation(multi_product_data, prompt, user_id)
            logger.info(f"PPT generated successfully: {ppt_path}")
        except Exception as e:
            logger.error(f"PPT generation failed: {str(e)}")
            raise Exception(f"Failed to generate presentation: {str(e)}")
        
        # Step 6: Finalize
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 'Finalizing presentation...', 'step': 6, 'total_steps': 6}
        )
        
        # Update generation record
        generation.status = "completed"
        generation.file_path = ppt_path
        generation.completed_at = datetime.utcnow()
        db.commit()
        
        # Generate download URL
        filename = os.path.basename(ppt_path)
        download_url = f"/api/ppt/download/{filename}"
        
        # Cleanup processed files
        try:
            multi_extractor.close()
        except Exception as e:
            logger.warning(f"Cleanup failed: {str(e)}")
        
        logger.info(f"PPT generation completed successfully for user {user_id}")
        
        return {
            "status": "completed",
            "download_url": download_url,
            "file_path": ppt_path,
            "filename": filename,
            "products_count": len(multi_product_data),
            "slide_count": generator.get_presentation_info(ppt_path).get('slide_count', 0)
        }
        
    except Exception as e:
        logger.error(f"PPT generation task failed: {str(e)}")
        
        # Update generation record with error
        try:
            generation = db.query(PPTGeneration).filter(PPTGeneration.id == generation_id).first()
            if generation:
                generation.status = "failed"
                generation.error_message = str(e)
                generation.completed_at = datetime.utcnow()
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update generation record: {str(db_error)}")
        
        # Update task state
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 'Generation failed'}
        )
        
        raise e
        
    finally:
        db.close()

@celery_app.task
def cleanup_old_files_task():
    """Clean up old generated files"""
    try:
        logger.info("Starting cleanup of old files")
        
        # Clean up files older than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        db = SessionLocal()
        
        try:
            # Find old generations
            old_generations = db.query(PPTGeneration).filter(
                PPTGeneration.created_at < cutoff_date,
                PPTGeneration.status.in_(["completed", "failed"])
            ).all()
            
            cleaned_count = 0
            
            for generation in old_generations:
                try:
                    # Delete file if it exists
                    if generation.file_path and os.path.exists(generation.file_path):
                        os.remove(generation.file_path)
                        logger.info(f"Deleted old file: {generation.file_path}")
                        cleaned_count += 1
                    
                    # Clear file path in database
                    generation.file_path = None
                    
                except Exception as e:
                    logger.warning(f"Failed to delete file {generation.file_path}: {str(e)}")
            
            db.commit()
            
            # Also clean up orphaned files in generated directory
            generated_dir = settings.generated_dir
            if os.path.exists(generated_dir):
                for filename in os.listdir(generated_dir):
                    file_path = os.path.join(generated_dir, filename)
                    
                    try:
                        # Check file age
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_mtime < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"Deleted orphaned file: {file_path}")
                            cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete orphaned file {file_path}: {str(e)}")
            
            # Clean up old upload files
            upload_dir = settings.upload_dir
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    file_path = os.path.join(upload_dir, filename)
                    
                    try:
                        # Check file age
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_mtime < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"Deleted old upload file: {file_path}")
                            cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete upload file {file_path}: {str(e)}")
            
            logger.info(f"Cleanup completed. Deleted {cleaned_count} files.")
            
            return {
                "status": "completed",
                "files_deleted": cleaned_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise e

@celery_app.task
def health_check_task():
    """Health check task for monitoring"""
    try:
        logger.info("Running health check task")
        
        # Check database connection
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        finally:
            db.close()
        
        # Check file system
        try:
            os.makedirs(settings.generated_dir, exist_ok=True)
            os.makedirs(settings.upload_dir, exist_ok=True)
            os.makedirs(settings.template_dir, exist_ok=True)
            fs_status = "healthy"
        except Exception as e:
            fs_status = f"unhealthy: {str(e)}"
        
        # Check AI service
        try:
            from ..ai.langchain_service import langchain_service
            ai_status = "healthy" if langchain_service.is_available() else "unavailable"
        except Exception as e:
            ai_status = f"unhealthy: {str(e)}"
        
        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": db_status,
                "filesystem": fs_status,
                "ai_service": ai_status
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Task for testing purposes
@celery_app.task
def test_task(message: str = "Hello from Celery!"):
    """Simple test task"""
    logger.info(f"Test task executed: {message}")
    return {
        "status": "completed",
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }