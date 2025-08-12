// API service for Lazulite backend integration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Check if we're in development mode
const isDevelopment = import.meta.env.NODE_ENV === 'development';

export interface ProductData {
  name: string;
  overview: string;
  specifications: Record<string, string>;
  content_integration: string[];
  infrastructure_requirements: string[];
  images: string[];
}

export interface ScrapedContent {
  overview: string;
  specifications: string[];
  content_integration: string[];
  infrastructure_requirements: string[];
}

export interface ProductContent {
  product_name: string;
  overview: string;
  specifications: string[];
  content_integration: string[];
  infrastructure_requirements: string[];
  images: string[];
  image_layout: string;
}

export interface MultiProductResponse {
  products: ProductContent[];
  total_products: number;
  extraction_status: string;
}

export interface PPTGenerationRequest {
  prompt: string;
  product_url?: string;
  approved_content?: ProductContent[];
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: string;
  download_url?: string;
  error_message?: string;
}

export class APIService {
  private static getAuthHeaders(): HeadersInit {
    // In production, get token from auth context
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  /**
   * Extract and summarize product content from Lazulite website
   */
  static async extractProductContent(productNames: string[]): Promise<MultiProductResponse> {
    try {
      // In development, check if backend is available
      if (isDevelopment) {
        const health = await this.healthCheck();
        if (!health.backend_available) {
          // Return simulated data for development
          return this.getSimulatedContent(productNames);
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/extract-content`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          product_names: productNames,
          base_url: 'https://lazulite.ae/activations',
          summarization_requirements: {
            overview_lines: 2,
            points_per_section: 2,
            sections: ['specifications', 'content_integration', 'infrastructure_requirements']
          }
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to extract product content');
      }

      return await response.json();
    } catch (error) {
      console.error('Content Extraction Error:', error);
      // Fallback to simulated content if backend fails
      return this.getSimulatedContent(productNames);
    }
  }

  /**
   * Get simulated content for development/demo purposes
   */
  private static getSimulatedContent(productNames: string[]): MultiProductResponse {
    const products: ProductContent[] = productNames.map((productName, index) => ({
      product_name: productName,
      overview: `${productName} offers cutting-edge interactive technology solutions designed for modern business environments. This product combines advanced AI capabilities with stunning visual displays to create engaging user experiences.`,
      specifications: [
        "High-resolution 4K display with multi-touch interface and gesture recognition",
        "AI-powered facial detection and real-time analytics with cloud connectivity"
      ],
      content_integration: [
        "Seamless CMS integration with real-time content updates and scheduling",
        "Multi-platform compatibility with cloud-based management dashboard"
      ],
      infrastructure_requirements: [
        "Stable internet connection (minimum 50 Mbps) with dedicated network access",
        "Dedicated power supply (220V) with UPS backup and climate control"
      ],
      images: [
        `https://via.placeholder.com/800x600/0066cc/ffffff?text=${encodeURIComponent(productName)}+Image+1`,
        `https://via.placeholder.com/800x600/6600cc/ffffff?text=${encodeURIComponent(productName)}+Image+2`
      ],
      image_layout: index === 0 ? "single" : index === 1 ? "side_by_side" : "grid"
    }));

    return {
      products,
      total_products: products.length,
      extraction_status: "completed"
    };
  }

  /**
   * Modify extracted content based on user feedback
   */
  static async modifyContent(
    content: ProductContent, 
    modifications: Record<string, any>
  ): Promise<ProductContent> {
    try {
      if (isDevelopment) {
        const health = await this.healthCheck();
        if (!health.backend_available) {
          // Apply modifications locally for demo
          return this.applyModificationsLocally(content, modifications);
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/modify-content?product_name=${encodeURIComponent(content.product_name)}`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          content,
          modifications
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to modify content');
      }

      return await response.json();
    } catch (error) {
      console.error('Content Modification Error:', error);
      return this.applyModificationsLocally(content, modifications);
    }
  }

  /**
   * Apply modifications locally for demo purposes
   */
  private static applyModificationsLocally(
    content: ProductContent, 
    modifications: Record<string, any>
  ): ProductContent {
    const modifiedContent = { ...content };
    
    // Apply modifications based on user input
    for (const [section, changes] of Object.entries(modifications)) {
      if (section in modifiedContent) {
        if (changes.action === 'replace') {
          (modifiedContent as any)[section] = changes.new_content;
        } else if (changes.action === 'add') {
          if (Array.isArray((modifiedContent as any)[section])) {
            (modifiedContent as any)[section].push(...changes.items);
          } else {
            (modifiedContent as any)[section] += ' ' + changes.text;
          }
        } else if (changes.action === 'delete') {
          if (Array.isArray((modifiedContent as any)[section])) {
            (modifiedContent as any)[section] = (modifiedContent as any)[section].filter(
              (item: string) => !changes.items.includes(item)
            );
          }
        }
      }
    }
    
    return modifiedContent;
  }

  /**
   * Generate PPT with approved content
   */
  static async generatePPT(request: PPTGenerationRequest): Promise<{ task_id: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ppt/generate`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          prompt: request.prompt,
          product_url: request.product_url || 'https://lazulite.ae/activations',
          approved_content: request.approved_content
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start PPT generation');
      }

      return await response.json();
    } catch (error) {
      console.error('PPT Generation Error:', error);
      throw error;
    }
  }

  /**
   * Check PPT generation status
   */
  static async checkPPTStatus(taskId: string): Promise<TaskStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ppt/status/${taskId}`, {
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to check status');
      }

      return await response.json();
    } catch (error) {
      console.error('Status Check Error:', error);
      throw error;
    }
  }

  /**
   * Send chat message (for content modification requests)
   */
  static async sendChatMessage(sessionId: string, message: string): Promise<{ response: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ content: message }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send message');
      }

      const data = await response.json();
      return { response: data.content };
    } catch (error) {
      console.error('Chat Message Error:', error);
      throw error;
    }
  }

  /**
   * Create new chat session
   */
  static async createChatSession(): Promise<{ session_id: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/sessions`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create chat session');
      }

      return await response.json();
    } catch (error) {
      console.error('Chat Session Error:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  static async healthCheck(): Promise<{ status: string; backend_available: boolean }> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        return { status: 'unhealthy', backend_available: false };
      }

      const data = await response.json();
      return { status: data.status, backend_available: true };
    } catch (error: any) {
      console.error('Health Check Error:', error);
      
      // Provide more specific error information
      if (error.name === 'AbortError') {
        console.error('Health check timed out after 5 seconds');
      } else if (error.message?.includes('fetch')) {
        console.error('Backend server is not running or not accessible at:', API_BASE_URL);
      }
      
      return { status: 'unhealthy', backend_available: false };
    }
  }
}