// API service for data-collector backend integration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export interface FileUploadResponse {
  file_id: string;
  filename: string;
  file_type: string;
  file_format: string;
  status: string;
  message: string;
  metadata?: {
    name?: string;
    version?: string;
    description?: string;
    base_url?: string;
  };
}

export interface ProcessingStatus {
  file_id: string;
  status: string;
  progress: number;
  message: string;
  result?: any;
  error?: string;
}

export interface ConvertRequest {
  file_id: string;
  show_metrics?: boolean;
}

export interface ConvertResponse {
  file_id: string;
  success: boolean;
  common_spec?: any;
  metrics?: any;
  error?: string;
}

export interface FileInfo {
  file_id: string;
  filename: string;
  file_type: string;
  file_format: string;
  file_size: number;
  upload_time: string;
  status: string;
  progress: number;
  message: string;
  metadata?: any;
}

class DataCollectorAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Upload file to the data-collector API
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  // Get list of uploaded files
  async getFiles(): Promise<{ files: FileInfo[] }> {
    const response = await fetch(`${this.baseUrl}/files`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch files');
    }

    return response.json();
  }

  // Get processing status for a specific file
  async getFileStatus(fileId: string): Promise<ProcessingStatus> {
    const response = await fetch(`${this.baseUrl}/files/${fileId}/status`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('File not found');
      }
      throw new Error('Failed to fetch file status');
    }

    return response.json();
  }

  // Convert file to CommonAPISpec
  async convertFile(fileId: string, showMetrics: boolean = false): Promise<ConvertResponse> {
    const response = await fetch(`${this.baseUrl}/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_id: fileId,
        show_metrics: showMetrics,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Conversion failed');
    }

    return response.json();
  }

  // Delete uploaded file
  async deleteFile(fileId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/files/${fileId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('File not found');
      }
      throw new Error('Failed to delete file');
    }

    return response.json();
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }
}

// Create singleton instance
export const dataCollectorAPI = new DataCollectorAPI();

// Hook for React components
export const useDataCollectorAPI = () => {
  return dataCollectorAPI;
};

export default dataCollectorAPI;
