from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator, EmailStr
import re
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class EmailValidator:
    """Email validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        try:
            # Basic email regex
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception:
            return False
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email address"""
        return email.lower().strip()

class PasswordValidator:
    """Password validation utilities"""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            "is_valid": True,
            "errors": [],
            "score": 0
        }
        
        if len(password) < 12:
            result["errors"].append("Password must be at least 12 characters long")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'[A-Z]', password):
            result["errors"].append("Password must contain at least 1 uppercase letter")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'[a-z]', password):
            result["errors"].append("Password must contain at least 1 lowercase letter")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'[0-9]', password):
            result["errors"].append("Password must contain at least 1 number")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["errors"].append("Password must contain at least 1 special character")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            result["errors"].append("Password should not contain repeated characters")
            result["score"] -= 1
        
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            result["errors"].append("Password should not contain sequential numbers")
            result["score"] -= 1
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            result["errors"].append("Password should not contain sequential letters")
            result["score"] -= 1
        
        # Common passwords check (simplified)
        common_passwords = [
            'password', '123456789', 'qwertyuiop', 'administrator',
            'welcome123', 'password123', 'admin123'
        ]
        
        if password.lower() in common_passwords:
            result["errors"].append("Password is too common")
            result["is_valid"] = False
            result["score"] = 0
        
        return result

class FileValidator:
    """File validation utilities"""
    
    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    ALLOWED_PPT_EXTENSIONS = ['.pptx', '.ppt']
    ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB
    
    @classmethod
    def validate_file_extension(cls, filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        
        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]
    
    @classmethod
    def validate_image_file(cls, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate image file"""
        result = {"is_valid": True, "errors": []}
        
        if not cls.validate_file_extension(filename, cls.ALLOWED_IMAGE_EXTENSIONS):
            result["errors"].append(f"Invalid image format. Allowed: {', '.join(cls.ALLOWED_IMAGE_EXTENSIONS)}")
            result["is_valid"] = False
        
        if file_size > cls.MAX_IMAGE_SIZE:
            result["errors"].append(f"Image too large. Maximum size: {cls.MAX_IMAGE_SIZE / (1024*1024):.1f}MB")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_ppt_file(cls, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate PowerPoint file"""
        result = {"is_valid": True, "errors": []}
        
        if not cls.validate_file_extension(filename, cls.ALLOWED_PPT_EXTENSIONS):
            result["errors"].append(f"Invalid PowerPoint format. Allowed: {', '.join(cls.ALLOWED_PPT_EXTENSIONS)}")
            result["is_valid"] = False
        
        if file_size > cls.MAX_FILE_SIZE:
            result["errors"].append(f"File too large. Maximum size: {cls.MAX_FILE_SIZE / (1024*1024):.1f}MB")
            result["is_valid"] = False
        
        return result
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
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

class URLValidator:
    """URL validation utilities"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        try:
            pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
            return bool(re.match(pattern, url))
        except Exception:
            return False
    
    @staticmethod
    def is_lazulite_url(url: str) -> bool:
        """Check if URL is from Lazulite domain"""
        try:
            return 'lazulite.ae' in url.lower()
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

class TextValidator:
    """Text content validation utilities"""
    
    @staticmethod
    def validate_prompt(prompt: str) -> Dict[str, Any]:
        """Validate user prompt"""
        result = {"is_valid": True, "errors": []}
        
        if not prompt or not prompt.strip():
            result["errors"].append("Prompt cannot be empty")
            result["is_valid"] = False
            return result
        
        prompt = prompt.strip()
        
        if len(prompt) < 10:
            result["errors"].append("Prompt must be at least 10 characters long")
            result["is_valid"] = False
        
        if len(prompt) > 1000:
            result["errors"].append("Prompt must be less than 1000 characters")
            result["is_valid"] = False
        
        # Check for potentially harmful content (basic)
        harmful_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe.*?>',
            r'<object.*?>',
            r'<embed.*?>'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                result["errors"].append("Prompt contains potentially harmful content")
                result["is_valid"] = False
                break
        
        return result
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove potentially harmful HTML/JS
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def validate_chat_message(message: str) -> Dict[str, Any]:
        """Validate chat message"""
        result = {"is_valid": True, "errors": []}
        
        if not message or not message.strip():
            result["errors"].append("Message cannot be empty")
            result["is_valid"] = False
            return result
        
        message = message.strip()
        
        if len(message) > 2000:
            result["errors"].append("Message must be less than 2000 characters")
            result["is_valid"] = False
        
        return result

class DataValidator:
    """General data validation utilities"""
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""
        try:
            import uuid
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_json_data(data: Any, required_fields: List[str] = None) -> Dict[str, Any]:
        """Validate JSON data structure"""
        result = {"is_valid": True, "errors": []}
        
        if not isinstance(data, dict):
            result["errors"].append("Data must be a JSON object")
            result["is_valid"] = False
            return result
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                result["errors"].append(f"Missing required fields: {', '.join(missing_fields)}")
                result["is_valid"] = False
        
        return result
    
    @staticmethod
    def validate_pagination(page: int, limit: int, max_limit: int = 100) -> Dict[str, Any]:
        """Validate pagination parameters"""
        result = {"is_valid": True, "errors": []}
        
        if page < 1:
            result["errors"].append("Page must be greater than 0")
            result["is_valid"] = False
        
        if limit < 1:
            result["errors"].append("Limit must be greater than 0")
            result["is_valid"] = False
        
        if limit > max_limit:
            result["errors"].append(f"Limit cannot exceed {max_limit}")
            result["is_valid"] = False
        
        return result

# Pydantic models for request validation
class UserRegistrationRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Full name must be less than 100 characters')
        return v.strip()
    
    @validator('password')
    def validate_password_strength(cls, v):
        validation = PasswordValidator.validate_password(v)
        if not validation['is_valid']:
            raise ValueError('; '.join(validation['errors']))
        return v

class PPTGenerationRequest(BaseModel):
    prompt: str
    product_url: Optional[str] = None
    
    @validator('prompt')
    def validate_prompt_content(cls, v):
        validation = TextValidator.validate_prompt(v)
        if not validation['is_valid']:
            raise ValueError('; '.join(validation['errors']))
        return TextValidator.clean_text(v)
    
    @validator('product_url')
    def validate_product_url(cls, v):
        if v is not None:
            if not URLValidator.is_valid_url(v):
                raise ValueError('Invalid URL format')
            if not URLValidator.is_lazulite_url(v):
                raise ValueError('URL must be from lazulite.ae domain')
            return URLValidator.normalize_url(v)
        return v

class ChatMessageRequest(BaseModel):
    content: str
    
    @validator('content')
    def validate_message_content(cls, v):
        validation = TextValidator.validate_chat_message(v)
        if not validation['is_valid']:
            raise ValueError('; '.join(validation['errors']))
        return TextValidator.clean_text(v)

# Validation helper functions
def validate_request_data(data: Dict[str, Any], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Generic request data validation"""
    result = {"is_valid": True, "errors": [], "cleaned_data": {}}
    
    try:
        for field, rules in validation_rules.items():
            value = data.get(field)
            
            # Check required fields
            if rules.get('required', False) and (value is None or value == ''):
                result["errors"].append(f"{field} is required")
                result["is_valid"] = False
                continue
            
            # Skip validation for optional empty fields
            if value is None or value == '':
                result["cleaned_data"][field] = value
                continue
            
            # Type validation
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                result["errors"].append(f"{field} must be of type {expected_type.__name__}")
                result["is_valid"] = False
                continue
            
            # Length validation for strings
            if isinstance(value, str):
                min_length = rules.get('min_length')
                max_length = rules.get('max_length')
                
                if min_length and len(value) < min_length:
                    result["errors"].append(f"{field} must be at least {min_length} characters long")
                    result["is_valid"] = False
                    continue
                
                if max_length and len(value) > max_length:
                    result["errors"].append(f"{field} must be less than {max_length} characters")
                    result["is_valid"] = False
                    continue
                
                # Clean text if specified
                if rules.get('clean_text', False):
                    value = TextValidator.clean_text(value)
            
            # Custom validation function
            custom_validator = rules.get('validator')
            if custom_validator:
                try:
                    validation_result = custom_validator(value)
                    if isinstance(validation_result, dict) and not validation_result.get('is_valid', True):
                        result["errors"].extend(validation_result.get('errors', []))
                        result["is_valid"] = False
                        continue
                except Exception as e:
                    result["errors"].append(f"{field} validation failed: {str(e)}")
                    result["is_valid"] = False
                    continue
            
            result["cleaned_data"][field] = value
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        result["errors"].append("Validation process failed")
        result["is_valid"] = False
    
    return result

# Export commonly used validators
__all__ = [
    'ValidationError',
    'EmailValidator',
    'PasswordValidator', 
    'FileValidator',
    'URLValidator',
    'TextValidator',
    'DataValidator',
    'UserRegistrationRequest',
    'PPTGenerationRequest',
    'ChatMessageRequest',
    'validate_request_data'
]