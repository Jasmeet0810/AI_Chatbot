export interface ProductData {
  name: string;
  overview: string;
  images: string[];
  specifications: Record<string, string>;
  contentIntegration: string[];
  infrastructureRequirements: string[];
}

export interface PPTGenerationRequest {
  prompt: string;
  productUrl?: string;
  template?: string;
}

export interface PPTGenerationResponse {
  success: boolean;
  downloadUrl?: string;
  error?: string;
}