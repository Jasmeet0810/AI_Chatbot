import boto3
import json
from typing import Dict, List, Optional, Any
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class BedrockService:
    def __init__(self):
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.aws_region = settings.aws_region
        
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            logger.warning("AWS credentials not configured")
            self.client = None
        else:
            try:
                # Initialize Bedrock client
                self.client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.aws_region
                )
                logger.info("Bedrock service initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock service: {str(e)}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.client is not None
    
    def generate_text(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate text using Claude via Bedrock"""
        if not self.is_available():
            logger.warning("Bedrock service not available")
            return "AI service not available"
        
        try:
            # Prepare the request for Claude
            body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
            }
            
            response = self.client.invoke_model(
                modelId="anthropic.claude-v2",
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('completion', '').strip()
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            return f"Error generating text: {str(e)}"
    
    def enhance_product_content(self, product_name: str, raw_content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance product content using Claude"""
        try:
            if not self.is_available():
                return self._fallback_enhancement(product_name, raw_content)
            
            # Generate enhanced overview
            overview_prompt = f"""
            Please enhance the following product overview for {product_name} to make it more professional and presentation-ready.
            Keep it to exactly 2 concise lines while preserving all important information.
            
            Original overview: {raw_content.get('overview', '')}
            
            Enhanced overview (exactly 2 lines):
            """
            
            enhanced_overview = self.generate_text(overview_prompt, max_tokens=200)
            
            # Generate enhanced specifications
            specs_prompt = f"""
            From the following specifications for {product_name}, create exactly 2 key technical specifications.
            Make them clear, concise, and professional for a business presentation.
            
            Original specifications: {str(raw_content.get('specifications', {}))}
            
            Top 2 specifications (as 2 separate lines):
            """
            
            enhanced_specs = self.generate_text(specs_prompt, max_tokens=200)
            specs_list = [line.strip() for line in enhanced_specs.split('\n') if line.strip()][:2]
            
            # Generate enhanced content integration
            integration_prompt = f"""
            From the following content integration information for {product_name}, create exactly 2 key integration features.
            Make them actionable and business-focused.
            
            Original content integration: {str(raw_content.get('content_integration', []))}
            
            Top 2 integration features (as 2 separate lines):
            """
            
            enhanced_integration = self.generate_text(integration_prompt, max_tokens=200)
            integration_list = [line.strip() for line in enhanced_integration.split('\n') if line.strip()][:2]
            
            # Generate enhanced infrastructure requirements
            infra_prompt = f"""
            From the following infrastructure requirements for {product_name}, create exactly 2 critical requirements.
            Make them specific and actionable for implementation.
            
            Original infrastructure requirements: {str(raw_content.get('infrastructure_requirements', []))}
            
            Top 2 infrastructure requirements (as 2 separate lines):
            """
            
            enhanced_infra = self.generate_text(infra_prompt, max_tokens=200)
            infra_list = [line.strip() for line in enhanced_infra.split('\n') if line.strip()][:2]
            
            return {
                'product_name': product_name,
                'overview': enhanced_overview,
                'specifications': specs_list if len(specs_list) >= 2 else self._get_fallback_specs(),
                'content_integration': integration_list if len(integration_list) >= 2 else self._get_fallback_integration(),
                'infrastructure_requirements': infra_list if len(infra_list) >= 2 else self._get_fallback_infrastructure(),
                'images': raw_content.get('images', []),
                'image_layout': self._determine_image_layout(len(raw_content.get('images', [])))
            }
            
        except Exception as e:
            logger.error(f"Content enhancement failed for {product_name}: {str(e)}")
            return self._fallback_enhancement(product_name, raw_content)
    
    def _fallback_enhancement(self, product_name: str, raw_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback enhanced content"""
        return {
            'product_name': product_name,
            'overview': f"{product_name} offers advanced interactive technology solutions. Designed for enhanced user engagement and seamless integration.",
            'specifications': self._get_fallback_specs(),
            'content_integration': self._get_fallback_integration(),
            'infrastructure_requirements': self._get_fallback_infrastructure(),
            'images': raw_content.get('images', []),
            'image_layout': self._determine_image_layout(len(raw_content.get('images', [])))
        }
    
    def _get_fallback_specs(self) -> List[str]:
        return [
            "High-resolution 4K display with multi-touch interface",
            "AI-powered analytics with real-time data processing"
        ]
    
    def _get_fallback_integration(self) -> List[str]:
        return [
            "Seamless CMS integration with real-time content updates",
            "Multi-platform compatibility with cloud management"
        ]
    
    def _get_fallback_infrastructure(self) -> List[str]:
        return [
            "Stable internet connection (minimum 50 Mbps)",
            "Dedicated power supply with backup systems"
        ]
    
    def _determine_image_layout(self, image_count: int) -> str:
        """Determine image layout based on count"""
        if image_count == 1:
            return "single"
        elif image_count == 2:
            return "side_by_side"
        elif image_count >= 3:
            return "grid"
        else:
            return "none"

# Global service instance
bedrock_service = BedrockService()