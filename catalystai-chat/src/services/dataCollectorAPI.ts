// API service for data-collector backend integration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Authentication token (in production, this would come from login)
let authToken = 'demo-token';

// User Management Interfaces
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  full_name: string;
  password: string;
  is_admin?: boolean;
}

export interface UserLogin {
  username: string;
  password: string;
}

// Application Management Interfaces
export interface Application {
  id: number;
  name: string;
  description?: string;
  sealid: string;
  owner_id: number;
  status: string;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  name: string;
  description?: string;
  sealid: string;
  metadata?: any;
}

export interface ApplicationUpdate {
  name?: string;
  description?: string;
  status?: string;
  metadata?: any;
}

// API Spec Management Interfaces
export interface APISpec {
  id: number;
  name: string;
  version: string;
  description?: string;
  api_type: string;
  format: string;
  base_url?: string;
  file_path?: string;
  file_size?: number;
  status: string;
  application_id: number;
  created_by_id: number;
  processing_status: string;
  processing_error?: string;
  chromadb_id?: string;
  created_at: string;
  updated_at: string;
}

export interface APISpecCreate {
  name: string;
  version?: string;
  description?: string;
  api_type: string;
  format: string;
  base_url?: string;
  application_id: number;
}

export interface APISpecUpdate {
  name?: string;
  version?: string;
  description?: string;
  status?: string;
  base_url?: string;
}

// File Upload Interfaces
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  file_type: string;
  file_format: string;
  file_size: number;
  upload_status: string;
  processing_status: string;
  error_message?: string;
  metadata?: any;
  created_at: string;
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
  api_spec_id?: number;
  common_spec?: any;
  metrics?: any;
  error?: string;
}

// List Response Interfaces
export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  size: number;
}

export interface ApplicationListResponse {
  applications: Application[];
  total: number;
  page: number;
  size: number;
}

export interface APISpecListResponse {
  api_specs: APISpec[];
  total: number;
  page: number;
  size: number;
}

export interface FileUploadListResponse {
  file_uploads: FileUploadResponse[];
  total: number;
  page: number;
  size: number;
}

class DataCollectorAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Authentication methods
  setAuthToken(token: string) {
    authToken = token;
  }

  getAuthToken(): string {
    return authToken;
  }

  private getHeaders(): HeadersInit {
    return {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    };
  }

  private getFormHeaders(): HeadersInit {
    return {
      'Authorization': `Bearer ${authToken}`,
    };
  }

  // User Management
  async createUser(user: UserCreate): Promise<User> {
    const response = await fetch(`${this.baseUrl}/users/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(user),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create user');
    }

    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${this.baseUrl}/users/me`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to get current user');
    }

    return response.json();
  }

  async listUsers(page: number = 1, size: number = 10): Promise<UserListResponse> {
    const response = await fetch(`${this.baseUrl}/users/?page=${page}&size=${size}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }

    return response.json();
  }

  // Application Management
  async createApplication(application: ApplicationCreate): Promise<Application> {
    const response = await fetch(`${this.baseUrl}/applications/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(application),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create application');
    }

    return response.json();
  }

  async listApplications(page: number = 1, size: number = 10): Promise<ApplicationListResponse> {
    const response = await fetch(`${this.baseUrl}/applications/?page=${page}&size=${size}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch applications');
    }

    return response.json();
  }

  async getApplication(appId: number): Promise<Application> {
    const response = await fetch(`${this.baseUrl}/applications/${appId}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Application not found');
      }
      throw new Error('Failed to fetch application');
    }

    return response.json();
  }

  async updateApplication(appId: number, update: ApplicationUpdate): Promise<Application> {
    const response = await fetch(`${this.baseUrl}/applications/${appId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(update),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update application');
    }

    return response.json();
  }

  // API Spec Management
  async listAPISpecs(appId: number, page: number = 1, size: number = 10): Promise<APISpecListResponse> {
    const response = await fetch(`${this.baseUrl}/applications/${appId}/api-specs?page=${page}&size=${size}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch API specs');
    }

    return response.json();
  }

  async getAPISpec(specId: number): Promise<APISpec> {
    const response = await fetch(`${this.baseUrl}/api-specs/${specId}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('API spec not found');
      }
      throw new Error('Failed to fetch API spec');
    }

    return response.json();
  }

  async updateAPISpec(specId: number, update: APISpecUpdate): Promise<APISpec> {
    const response = await fetch(`${this.baseUrl}/api-specs/${specId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(update),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update API spec');
    }

    return response.json();
  }

  // File Upload Management
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      headers: this.getFormHeaders(),
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  async listFiles(page: number = 1, size: number = 10): Promise<FileUploadListResponse> {
    const response = await fetch(`${this.baseUrl}/files?page=${page}&size=${size}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch files');
    }

    return response.json();
  }

  async getFileStatus(fileId: string): Promise<ProcessingStatus> {
    const response = await fetch(`${this.baseUrl}/files/${fileId}/status`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('File not found');
      }
      throw new Error('Failed to fetch file status');
    }

    return response.json();
  }

  async convertFile(fileId: string, showMetrics: boolean = false): Promise<ConvertResponse> {
    const response = await fetch(`${this.baseUrl}/convert`, {
      method: 'POST',
      headers: this.getHeaders(),
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

  async deleteFile(fileId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/files/${fileId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
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