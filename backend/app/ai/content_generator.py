from typing import Dict, List, Any, Optional
from .langchain_service import langchain_service
from .prompts import get_prompt_template
import logging

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.langchain = langchain_service
    
    def enhance_content(self, product_data: Dict, user_prompt: str) -> Dict[str, Any]:
        """Use AI to enhance and format content for presentation"""
        try:
            logger.info("Starting content enhancement with AI")
            
            enhanced = {}
            
            # Generate title and subtitle
            enhanced.update(self._generate_titles(product_data, user_prompt))
            
            # Enhance overview
            enhanced['overview_text'] = self._enhance_overview(
                product_data.get('name', ''),
                product_data.get('overview', ''),
                user_prompt
            )
            
            # Enhance specifications
            enhanced['specifications_text'] = self._enhance_specifications(
                product_data.get('specifications', {}),
                user_prompt
            )
            
            # Enhance content integration
            enhanced['integration_text'] = self._enhance_content_integration(
                product_data.get('content_integration', []),
                product_data.get('name', ''),
                user_prompt
            )
            
            # Enhance infrastructure requirements
            enhanced['infrastructure_text'] = self._enhance_infrastructure(
                product_data.get('infrastructure_requirements', []),
                product_data.get('name', ''),
                user_prompt
            )
            
            # Process images
            enhanced['images'] = self._process_images(product_data.get('images', {}))
            
            # Generate executive summary
            enhanced['executive_summary'] = self._generate_executive_summary(
                product_data, user_prompt
            )
            
            logger.info("Content enhancement completed successfully")
            return enhanced
            
        except Exception as e:
            logger.error(f"Content enhancement failed: {str(e)}")
            # Return fallback content
            return self._generate_fallback_content(product_data, user_prompt)
    
    def enhance_multi_product_content(self, multi_product_data: List[Dict], user_prompt: str) -> Dict[str, Any]:
        """Enhance content for multiple products"""
        try:
            logger.info(f"Starting multi-product content enhancement for {len(multi_product_data)} products")
            
            # Generate overall presentation title
            product_names = [product.get('product_name', 'Product') for product in multi_product_data]
            
            if len(product_names) == 1:
                title = f"{product_names[0]} Presentation"
            elif len(product_names) == 2:
                title = f"{product_names[0]} & {product_names[1]} Presentation"
            else:
                title = f"Multi-Product Presentation: {', '.join(product_names[:2])} & More"
            
            enhanced = {
                'title': title,
                'subtitle': f'Powered by Lazulite AI Technology - {len(product_names)} Products',
                'products': multi_product_data,
                'total_products': len(multi_product_data)
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
    
    def _generate_titles(self, product_data: Dict, user_prompt: str) -> Dict[str, str]:
        """Generate presentation title and subtitle"""
        try:
            if not self.langchain.is_available():
                return self._fallback_titles(product_data)
            
            # Generate title
            title_prompt = get_prompt_template('title_generation')
            title_chain = self.langchain.create_chain(title_prompt.template)
            
            if title_chain:
                title_response = self.langchain.run_chain(
                    title_chain,
                    product_name=product_data.get('name', 'Lazulite Product'),
                    user_prompt=user_prompt,
                    key_features=', '.join(list(product_data.get('specifications', {}).keys())[:3])
                )
                
                # Extract first title from response
                titles = title_response.split('\n')
                main_title = titles[0].strip() if titles else f"{product_data.get('name', 'Lazulite Product')} Presentation"
                
                # Clean up title
                main_title = main_title.replace('1. ', '').replace('• ', '').strip()
                
                return {
                    'title': main_title,
                    'subtitle': 'Powered by Lazulite AI Technology'
                }
            
        except Exception as e:
            logger.warning(f"Title generation failed: {str(e)}")
        
        return self._fallback_titles(product_data)
    
    def _enhance_overview(self, product_name: str, raw_overview: str, user_prompt: str) -> str:
        """Enhance product overview"""
        try:
            if not self.langchain.is_available() or not raw_overview:
                return raw_overview or "Product overview not available"
            
            overview_prompt = get_prompt_template('overview_enhancement')
            overview_chain = self.langchain.create_chain(overview_prompt.template)
            
            if overview_chain:
                enhanced_overview = self.langchain.run_chain(
                    overview_chain,
                    product_name=product_name,
                    raw_overview=raw_overview,
                    user_prompt=user_prompt
                )
                
                return enhanced_overview
                
        except Exception as e:
            logger.warning(f"Overview enhancement failed: {str(e)}")
        
        return raw_overview or "Product overview not available"
    
    def _enhance_specifications(self, specifications: Dict[str, str], user_prompt: str) -> str:
        """Convert specifications to professional sentences"""
        try:
            if not specifications:
                return "Specifications not available"
            
            if not self.langchain.is_available():
                return self._format_specifications_fallback(specifications)
            
            specs_prompt = get_prompt_template('specifications_enhancement')
            specs_chain = self.langchain.create_chain(specs_prompt.template)
            
            if specs_chain:
                # Convert dict to string format
                specs_text = '\n'.join([f"{k}: {v}" for k, v in specifications.items()])
                
                enhanced_specs = self.langchain.run_chain(
                    specs_chain,
                    specifications=specs_text,
                    user_prompt=user_prompt
                )
                
                return enhanced_specs
                
        except Exception as e:
            logger.warning(f"Specifications enhancement failed: {str(e)}")
        
        return self._format_specifications_fallback(specifications)
    
    def _enhance_content_integration(self, content_integration: List[str], product_name: str, user_prompt: str) -> str:
        """Enhance content integration information"""
        try:
            if not content_integration:
                return "Content integration information not available"
            
            if not self.langchain.is_available():
                return self._format_list_fallback(content_integration, "Content Integration Features")
            
            integration_prompt = get_prompt_template('content_integration_enhancement')
            integration_chain = self.langchain.create_chain(integration_prompt.template)
            
            if integration_chain:
                integration_text = '\n'.join(content_integration)
                
                enhanced_integration = self.langchain.run_chain(
                    integration_chain,
                    content_integration=integration_text,
                    product_name=product_name,
                    user_prompt=user_prompt
                )
                
                return enhanced_integration
                
        except Exception as e:
            logger.warning(f"Content integration enhancement failed: {str(e)}")
        
        return self._format_list_fallback(content_integration, "Content Integration Features")
    
    def _enhance_infrastructure(self, infrastructure: List[str], product_name: str, user_prompt: str) -> str:
        """Enhance infrastructure requirements"""
        try:
            if not infrastructure:
                return "Infrastructure requirements not available"
            
            if not self.langchain.is_available():
                return self._format_list_fallback(infrastructure, "Infrastructure Requirements")
            
            infra_prompt = get_prompt_template('infrastructure_enhancement')
            infra_chain = self.langchain.create_chain(infra_prompt.template)
            
            if infra_chain:
                infra_text = '\n'.join(infrastructure)
                
                enhanced_infra = self.langchain.run_chain(
                    infra_chain,
                    infrastructure_requirements=infra_text,
                    product_name=product_name,
                    user_prompt=user_prompt
                )
                
                return enhanced_infra
                
        except Exception as e:
            logger.warning(f"Infrastructure enhancement failed: {str(e)}")
        
        return self._format_list_fallback(infrastructure, "Infrastructure Requirements")
    
    def _process_images(self, images_data: Dict) -> List[str]:
        """Process image data for presentation"""
        try:
            if isinstance(images_data, dict):
                return images_data.get('processed_paths', [])
            elif isinstance(images_data, list):
                return images_data
            else:
                return []
        except Exception as e:
            logger.warning(f"Image processing failed: {str(e)}")
            return []
    
    def _generate_executive_summary(self, product_data: Dict, user_prompt: str) -> str:
        """Generate executive summary"""
        try:
            if not self.langchain.is_available():
                return self._fallback_executive_summary(product_data)
            
            summary_prompt = get_prompt_template('executive_summary')
            summary_chain = self.langchain.create_chain(summary_prompt.template)
            
            if summary_chain:
                # Prepare specifications summary
                specs = product_data.get('specifications', {})
                specs_summary = ', '.join([f"{k}: {v}" for k, v in list(specs.items())[:3]])
                
                executive_summary = self.langchain.run_chain(
                    summary_chain,
                    product_name=product_data.get('name', 'Lazulite Product'),
                    overview=product_data.get('overview', '')[:500],  # Limit length
                    specifications=specs_summary,
                    user_prompt=user_prompt
                )
                
                return executive_summary
                
        except Exception as e:
            logger.warning(f"Executive summary generation failed: {str(e)}")
        
        return self._fallback_executive_summary(product_data)
    
    # Fallback methods for when AI is not available
    
    def _fallback_titles(self, product_data: Dict) -> Dict[str, str]:
        """Generate fallback titles"""
        product_name = product_data.get('name', 'Lazulite Product')
        return {
            'title': f"{product_name} Presentation",
            'subtitle': 'Powered by Lazulite AI Technology'
        }
    
    def _format_specifications_fallback(self, specifications: Dict[str, str]) -> str:
        """Format specifications without AI enhancement"""
        if not specifications:
            return "Specifications not available"
        
        formatted_specs = []
        for key, value in specifications.items():
            formatted_specs.append(f"• {key}: {value}")
        
        return '\n'.join(formatted_specs)
    
    def _format_list_fallback(self, items: List[str], title: str) -> str:
        """Format list items without AI enhancement"""
        if not items:
            return f"{title} not available"
        
        formatted_items = [f"• {item}" for item in items if item.strip()]
        return '\n'.join(formatted_items)
    
    def _fallback_executive_summary(self, product_data: Dict) -> str:
        """Generate fallback executive summary"""
        product_name = product_data.get('name', 'Lazulite Product')
        overview = product_data.get('overview', '')
        
        if overview:
            # Take first sentence or first 100 characters
            summary = overview.split('.')[0] + '.' if '.' in overview else overview[:100] + '...'
        else:
            summary = f"{product_name} offers advanced technology solutions for modern business needs."
        
        return summary
    
    def _generate_fallback_content(self, product_data: Dict, user_prompt: str) -> Dict[str, Any]:
        """Generate fallback content when AI is not available"""
        logger.info("Generating fallback content (AI not available)")
        
        return {
            'title': f"{product_data.get('name', 'Lazulite Product')} Presentation",
            'subtitle': 'Powered by Lazulite AI Technology',
            'overview_text': product_data.get('overview', 'Product overview not available'),
            'specifications_text': self._format_specifications_fallback(product_data.get('specifications', {})),
            'integration_text': self._format_list_fallback(product_data.get('content_integration', []), 'Content Integration'),
            'infrastructure_text': self._format_list_fallback(product_data.get('infrastructure_requirements', []), 'Infrastructure Requirements'),
            'images': self._process_images(product_data.get('images', {})),
            'executive_summary': self._fallback_executive_summary(product_data)
        }
    
    def generate_chat_response(self, user_message: str, context: Dict = None) -> str:
        """Generate chat response"""
        try:
            if not self.langchain.is_available():
                return self._fallback_chat_response(user_message)
            
            chat_prompt = get_prompt_template('chat_response')
            chat_chain = self.langchain.create_chain(chat_prompt.template)
            
            if chat_chain:
                response = self.langchain.run_chain(
                    chat_chain,
                    user_message=user_message,
                    context=str(context or {})
                )
                
                return response
                
        except Exception as e:
            logger.warning(f"Chat response generation failed: {str(e)}")
        
        return self._fallback_chat_response(user_message)
    
    def _fallback_chat_response(self, user_message: str) -> str:
        """Generate fallback chat response"""
        return f"I understand you want to create a presentation. I'll help you generate a professional PowerPoint based on Lazulite product data. Please wait while I process your request: '{user_message}'"