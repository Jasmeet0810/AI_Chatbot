// API service for backend integration
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

export class APIService {
  static async generatePPT(prompt: string): Promise<{ downloadUrl: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-ppt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          source_url: 'https://lazulite.ae/activations',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate PPT');
      }

      return await response.json();
    } catch (error) {
      console.error('PPT Generation Error:', error);
      throw error;
    }
  }

  static async extractProductData(productUrl: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/extract-product`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: productUrl }),
      });

      if (!response.ok) {
        throw new Error('Failed to extract product data');
      }

      return await response.json();
    } catch (error) {
      console.error('Product Extraction Error:', error);
      throw error;
    }
  }
}