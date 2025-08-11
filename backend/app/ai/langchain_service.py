from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, List, Optional, Any
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class LangChainService:
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured")
            self.llm = None
            self.chat_model = None
        else:
            try:
                # Initialize models
                self.llm = OpenAI(
                    openai_api_key=self.openai_api_key,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                self.chat_model = ChatOpenAI(
                    openai_api_key=self.openai_api_key,
                    model_name="gpt-3.5-turbo",
                    temperature=0.7,
                    max_tokens=2000
                )
                
                logger.info("LangChain service initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize LangChain service: {str(e)}")
                self.llm = None
                self.chat_model = None
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.llm is not None and self.chat_model is not None
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the LLM"""
        if not self.is_available():
            logger.warning("LangChain service not available")
            return "AI service not available"
        
        try:
            response = self.llm(prompt, **kwargs)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            return f"Error generating text: {str(e)}"
    
    def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat completion"""
        if not self.is_available():
            logger.warning("LangChain service not available")
            return "AI service not available"
        
        try:
            # Convert messages to LangChain format
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            response = self.chat_model(langchain_messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            return f"Error in chat completion: {str(e)}"
    
    def run_chain(self, chain: LLMChain, **inputs) -> str:
        """Run a LangChain chain"""
        if not self.is_available():
            logger.warning("LangChain service not available")
            return "AI service not available"
        
        try:
            result = chain.run(**inputs)
            return result.strip()
            
        except Exception as e:
            logger.error(f"Chain execution failed: {str(e)}")
            return f"Error running chain: {str(e)}"
    
    def create_chain(self, prompt_template: str, **kwargs) -> Optional[LLMChain]:
        """Create a LangChain chain"""
        if not self.is_available():
            return None
        
        try:
            prompt = PromptTemplate.from_template(prompt_template)
            chain = LLMChain(llm=self.llm, prompt=prompt, **kwargs)
            return chain
            
        except Exception as e:
            logger.error(f"Failed to create chain: {str(e)}")
            return None
    
    def create_chat_chain(self, system_message: str, human_template: str) -> Optional[LLMChain]:
        """Create a chat-based chain"""
        if not self.is_available():
            return None
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", human_template)
            ])
            
            chain = LLMChain(llm=self.chat_model, prompt=prompt)
            return chain
            
        except Exception as e:
            logger.error(f"Failed to create chat chain: {str(e)}")
            return None
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text content"""
        if not text or not text.strip():
            return "No content to summarize"
        
        prompt = f"""
        Please summarize the following text in a clear, professional manner. 
        Keep the summary under {max_length} words and focus on the key points.
        
        Text to summarize:
        {text}
        
        Summary:
        """
        
        return self.generate_text(prompt)
    
    def enhance_bullet_points(self, bullet_points: List[str]) -> List[str]:
        """Enhance bullet points for better presentation"""
        if not bullet_points:
            return []
        
        enhanced_points = []
        
        for point in bullet_points:
            if not point.strip():
                continue
                
            prompt = f"""
            Enhance the following bullet point to make it more professional and presentation-ready.
            Keep it concise but impactful. Return only the enhanced bullet point.
            
            Original: {point}
            
            Enhanced:
            """
            
            enhanced = self.generate_text(prompt)
            enhanced_points.append(enhanced)
        
        return enhanced_points
    
    def generate_presentation_outline(self, topic: str, sections: List[str]) -> Dict[str, str]:
        """Generate presentation outline"""
        prompt = f"""
        Create a professional presentation outline for the topic: "{topic}"
        
        The presentation should include these sections:
        {', '.join(sections)}
        
        For each section, provide:
        1. A compelling title
        2. 3-4 key points to cover
        
        Format as a structured outline.
        """
        
        outline_text = self.generate_text(prompt)
        
        # Parse the outline (simplified)
        return {
            "topic": topic,
            "outline": outline_text,
            "sections": sections
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            "service_available": self.is_available(),
            "models": {
                "llm": "OpenAI GPT-3.5" if self.llm else None,
                "chat": "OpenAI GPT-3.5-turbo" if self.chat_model else None
            },
            "api_key_configured": bool(self.openai_api_key)
        }

# Global service instance
langchain_service = LangChainService()