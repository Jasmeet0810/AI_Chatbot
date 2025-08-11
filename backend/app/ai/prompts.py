from typing import Dict, List
from langchain.prompts import PromptTemplate

class PPTPrompts:
    """Collection of prompts for PPT generation"""
    
    # Product Overview Enhancement
    OVERVIEW_ENHANCEMENT = """
    You are a professional presentation writer specializing in technology products.
    
    Create a compelling product overview for {product_name} based on the following information:
    
    Raw Overview: {raw_overview}
    User Request: {user_prompt}
    
    Requirements:
    - Write in a professional, business-appropriate tone
    - Focus on key benefits and unique selling points
    - Make it suitable for a business presentation
    - Keep it between 100-200 words
    - Use clear, jargon-free language
    
    Enhanced Overview:
    """
    
    # Specifications Enhancement
    SPECIFICATIONS_ENHANCEMENT = """
    Convert the following technical specifications into well-written, professional sentences 
    suitable for a business presentation.
    
    Specifications: {specifications}
    Context: {user_prompt}
    
    Requirements:
    - Transform each specification into a complete, professional sentence
    - Make technical details accessible to business audiences
    - Maintain accuracy while improving readability
    - Group related specifications logically
    - Use bullet points for clarity
    
    Enhanced Specifications:
    """
    
    # Content Integration Enhancement
    CONTENT_INTEGRATION_ENHANCEMENT = """
    Enhance the following content integration information for a professional presentation:
    
    Raw Content Integration: {content_integration}
    Product Context: {product_name}
    User Request: {user_prompt}
    
    Requirements:
    - Explain integration capabilities clearly
    - Focus on business benefits
    - Use professional language
    - Organize information logically
    - Highlight key integration features
    
    Enhanced Content Integration:
    """
    
    # Infrastructure Requirements Enhancement
    INFRASTRUCTURE_ENHANCEMENT = """
    Improve the following infrastructure requirements for a business presentation:
    
    Raw Requirements: {infrastructure_requirements}
    Product: {product_name}
    Context: {user_prompt}
    
    Requirements:
    - Present technical requirements in business-friendly language
    - Organize by importance or category
    - Include implementation considerations
    - Make it actionable for decision-makers
    - Use clear, structured format
    
    Enhanced Infrastructure Requirements:
    """
    
    # Presentation Title Generation
    TITLE_GENERATION = """
    Generate a compelling presentation title based on:
    
    Product: {product_name}
    User Request: {user_prompt}
    Key Features: {key_features}
    
    Requirements:
    - Professional and engaging
    - Suitable for business presentation
    - Reflects the product's value proposition
    - Maximum 10 words
    
    Suggested Titles (provide 3 options):
    """
    
    # Slide Content Generation
    SLIDE_CONTENT_GENERATION = """
    Create content for a presentation slide with the following requirements:
    
    Slide Topic: {slide_topic}
    Product: {product_name}
    Raw Data: {raw_data}
    User Context: {user_prompt}
    
    Requirements:
    - Create a compelling slide title
    - Provide 4-6 key points for the slide
    - Use professional, presentation-appropriate language
    - Focus on business value and benefits
    - Make content visually presentable
    
    Slide Content:
    Title: [slide title]
    
    Key Points:
    • [point 1]
    • [point 2]
    • [point 3]
    • [point 4]
    """
    
    # Executive Summary Generation
    EXECUTIVE_SUMMARY = """
    Create an executive summary for a presentation about {product_name}:
    
    Product Overview: {overview}
    Key Specifications: {specifications}
    User Requirements: {user_prompt}
    
    Requirements:
    - Summarize in 3-4 sentences
    - Focus on business value and ROI
    - Highlight competitive advantages
    - Use executive-level language
    
    Executive Summary:
    """
    
    # Call to Action Generation
    CALL_TO_ACTION = """
    Generate a compelling call-to-action for a presentation about {product_name}:
    
    Context: {user_prompt}
    Key Benefits: {key_benefits}
    Target Audience: Business decision-makers
    
    Requirements:
    - Create urgency and interest
    - Include next steps
    - Professional tone
    - Action-oriented language
    
    Call to Action:
    """

class ChatPrompts:
    """Collection of prompts for chat interactions"""
    
    SYSTEM_MESSAGE = """
    You are an AI assistant specialized in creating professional PowerPoint presentations 
    for Lazulite technology products. You help users generate compelling, business-focused 
    presentations by extracting and enhancing product information.
    
    Your capabilities:
    - Extract product data from Lazulite website
    - Convert technical specifications into business-friendly content
    - Create professional presentation structures
    - Enhance content for executive audiences
    - Generate compelling titles and summaries
    
    Always maintain a professional, helpful tone and focus on business value.
    """
    
    CHAT_RESPONSE = """
    Based on the user's request: "{user_message}"
    
    Context: {context}
    
    Provide a helpful, professional response that:
    - Addresses the user's specific needs
    - Explains what you can do to help
    - Asks clarifying questions if needed
    - Maintains a conversational but professional tone
    
    Response:
    """
    
    PPT_GENERATION_STATUS = """
    The user has requested PPT generation with the prompt: "{user_prompt}"
    
    Current status: {status}
    Progress: {progress}
    
    Provide an informative update that:
    - Explains the current progress
    - Mentions what's happening next
    - Maintains user engagement
    - Sets appropriate expectations
    
    Status Update:
    """

def get_prompt_template(prompt_name: str) -> PromptTemplate:
    """Get a LangChain PromptTemplate by name"""
    
    prompt_mapping = {
        'overview_enhancement': PPTPrompts.OVERVIEW_ENHANCEMENT,
        'specifications_enhancement': PPTPrompts.SPECIFICATIONS_ENHANCEMENT,
        'content_integration_enhancement': PPTPrompts.CONTENT_INTEGRATION_ENHANCEMENT,
        'infrastructure_enhancement': PPTPrompts.INFRASTRUCTURE_ENHANCEMENT,
        'title_generation': PPTPrompts.TITLE_GENERATION,
        'slide_content_generation': PPTPrompts.SLIDE_CONTENT_GENERATION,
        'executive_summary': PPTPrompts.EXECUTIVE_SUMMARY,
        'call_to_action': PPTPrompts.CALL_TO_ACTION,
        'chat_response': ChatPrompts.CHAT_RESPONSE,
        'ppt_generation_status': ChatPrompts.PPT_GENERATION_STATUS,
    }
    
    if prompt_name not in prompt_mapping:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    
    return PromptTemplate.from_template(prompt_mapping[prompt_name])

def get_all_prompts() -> Dict[str, str]:
    """Get all available prompts"""
    return {
        'ppt_prompts': {
            'overview_enhancement': PPTPrompts.OVERVIEW_ENHANCEMENT,
            'specifications_enhancement': PPTPrompts.SPECIFICATIONS_ENHANCEMENT,
            'content_integration_enhancement': PPTPrompts.CONTENT_INTEGRATION_ENHANCEMENT,
            'infrastructure_enhancement': PPTPrompts.INFRASTRUCTURE_ENHANCEMENT,
            'title_generation': PPTPrompts.TITLE_GENERATION,
            'slide_content_generation': PPTPrompts.SLIDE_CONTENT_GENERATION,
            'executive_summary': PPTPrompts.EXECUTIVE_SUMMARY,
            'call_to_action': PPTPrompts.CALL_TO_ACTION,
        },
        'chat_prompts': {
            'system_message': ChatPrompts.SYSTEM_MESSAGE,
            'chat_response': ChatPrompts.CHAT_RESPONSE,
            'ppt_generation_status': ChatPrompts.PPT_GENERATION_STATUS,
        }
    }