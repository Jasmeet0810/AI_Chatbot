from typing import Dict, List, Any
from .bedrock_service import bedrock_service
import logging

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.bedrock = bedrock_service
    
    def enhance_multi_product_content(self, multi_product_data: List[Dict[str, Any]], user_prompt: str) -> Dict[str, Any]:
        """Enhance content for multiple products using Bedrock Claude"""
        try:
            logger.info(f"Starting multi-product content enhancement for {len(multi_product_data)} products")
            
            enhanced_products = []
            
            for product_data in multi_product_data:
                enhanced_product = self.bedrock.enhance_product_content(
                    product_data.get('name', 'Product'),
                    product_data
                )
                enhanced_products.append(enhanced_product)
            
            # Generate overall presentation title
            product_names = [product.get('product_name', 'Product') for product in enhanced_products]
            
            if len(product_names) == 1:
                title = f"{product_names[0]} Presentation"
            elif len(product_names) == 2:
                title = f"{product_names[0]} & {product_names[1]} Presentation"
            else:
                title = f"Multi-Product Presentation: {', '.join(product_names[:2])} & More"
            
            enhanced = {
                'title': title,
                'subtitle': f'Powered by Lazulite AI Technology - {len(product_names)} Products',
                'products': enhanced_products,
                'total_products': len(enhanced_products)
            }
            
            logger.info("Multi-product content enhancement completed successfully")
            return enhanced
            
        except Exception as e:
            logger.error(f"Multi-product content enhancement failed: {str(e)}")
            return {
                'title': 'Lazulite Product Presentation',
                'subtitle': 'Powered by Lazulite AI Technology',
                'products': multi_product_data,
                'total_products': len(multi_product_data)
            }
    
    def generate_chat_response(self, user_message: str, context: Dict = None) -> str:
        """Generate chat response using Bedrock Claude"""
        try:
            if not self.bedrock.is_available():
                return self._fallback_chat_response(user_message)
            
            prompt = f"""
            You are an AI assistant specialized in creating professional PowerPoint presentations 
            for Lazulite technology products. 
            
            User message: {user_message}
            Context: {str(context or {})}
            
            Provide a helpful, professional response that addresses the user's needs regarding 
            PPT generation and content modification.
            """
            
            response = self.bedrock.generate_text(prompt)
            return response
                
        except Exception as e:
            logger.warning(f"Chat response generation failed: {str(e)}")
            return self._fallback_chat_response(user_message)
    
    def _fallback_chat_response(self, user_message: str) -> str:
        """Generate fallback chat response"""
        return f"I understand you want to create a presentation. I'll help you generate a professional PowerPoint based on Lazulite product data. Please wait while I process your request: '{user_message}'"