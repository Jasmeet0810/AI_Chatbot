import os
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.generated_dir = settings.generated_dir
        self.template_dir = settings.template_dir
        self.max_file_size = settings.max_file_size
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [self.upload_dir, self.generated_dir, self.template_dir]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")
                raise Exception(f"Directory creation failed: {str(e)}")
    
    def save_uploaded_file(self, file_content: bytes, filename: str, user_id: str = None) -> str:
        """Save uploaded file to upload directory"""
        try:
            # Sanitize filename
            safe_filename = self._sanitize_filename(filename)
            
            # Add user prefix if provided
            if user_id:
                safe_filename = f"{user_id}_{safe_filename}"
            
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(safe_filename)
            safe_filename = f"{name}_{timestamp}{ext}"
            
            file_path = os.path.join(self.upload_dir, safe_filename)
            
            # Check file size
            if len(file_content) > self.max_file_size:
                raise Exception(f"File too large. Maximum size: {self.max_file_size} bytes")
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {str(e)}")
            raise Exception(f"File save failed: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file safely"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found for deletion: {file_path}")
                return False
            
            # Security check: ensure file is in allowed directories
            allowed_dirs = [self.upload_dir, self.generated_dir]
            if not any(os.path.commonpath([file_path, allowed_dir]) == allowed_dir for allowed_dir in allowed_dirs):
                logger.error(f"Attempted to delete file outside allowed directories: {file_path}")
                return False
            
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
    
    def delete_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """Delete multiple files"""
        results = {}
        
        for file_path in file_paths:
            results[file_path] = self.delete_file(file_path)
        
        return results
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": os.path.isfile(file_path),
                "extension": os.path.splitext(file_path)[1].lower()
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            return None
    
    def list_directory_files(self, directory: str, extension_filter: List[str] = None) -> List[Dict[str, Any]]:
        """List files in a directory with optional extension filter"""
        try:
            if not os.path.exists(directory):
                return []
            
            files = []
            
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                # Apply extension filter if provided
                if extension_filter:
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext not in extension_filter:
                        continue
                
                file_info = self.get_file_info(file_path)
                if file_info:
                    files.append(file_info)
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list directory files: {str(e)}")
            return []
    
    def cleanup_old_files(self, directory: str, max_age_days: int = 7) -> int:
        """Clean up files older than specified days"""
        try:
            if not os.path.exists(directory):
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0
            
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                try:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Deleted old file: {file_path}")
                        deleted_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to delete old file {file_path}: {str(e)}")
            
            logger.info(f"Cleanup completed. Deleted {deleted_count} files from {directory}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cleanup failed for directory {directory}: {str(e)}")
            return 0
    
    def get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        try:
            total_size = 0
            
            if not os.path.exists(directory):
                return 0
            
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue
            
            return total_size
            
        except Exception as e:
            logger.error(f"Failed to get directory size: {str(e)}")
            return 0
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy file from source to destination"""
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            shutil.copy2(source_path, destination_path)
            logger.info(f"File copied: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file: {str(e)}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move file from source to destination"""
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source_path, destination_path)
            logger.info(f"File moved: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file: {str(e)}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations"""
        import re
        
        if not filename:
            return "file"
        
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[^\w\s.-]', '', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 50:
            name = name[:50]
        
        return name + ext
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {}
            
            directories = {
                'uploads': self.upload_dir,
                'generated': self.generated_dir,
                'templates': self.template_dir
            }
            
            for name, directory in directories.items():
                if os.path.exists(directory):
                    files = self.list_directory_files(directory)
                    size = self.get_directory_size(directory)
                    
                    stats[name] = {
                        'directory': directory,
                        'file_count': len(files),
                        'total_size': size,
                        'total_size_mb': round(size / (1024 * 1024), 2)
                    }
                else:
                    stats[name] = {
                        'directory': directory,
                        'file_count': 0,
                        'total_size': 0,
                        'total_size_mb': 0
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {}
    
    def validate_file_type(self, filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file type based on extension"""
        if not filename:
            return False
        
        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]
    
    def is_safe_path(self, file_path: str) -> bool:
        """Check if file path is safe (no path traversal)"""
        try:
            # Resolve the path
            resolved_path = os.path.abspath(file_path)
            
            # Check if it's within allowed directories
            allowed_dirs = [
                os.path.abspath(self.upload_dir),
                os.path.abspath(self.generated_dir),
                os.path.abspath(self.template_dir)
            ]
            
            return any(
                os.path.commonpath([resolved_path, allowed_dir]) == allowed_dir
                for allowed_dir in allowed_dirs
            )
            
        except Exception as e:
            logger.error(f"Path safety check failed: {str(e)}")
            return False

# Global file manager instance
file_manager = FileManager()