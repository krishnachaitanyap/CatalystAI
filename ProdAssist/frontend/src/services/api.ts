import axios, { AxiosInstance, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';
import {
  User,
  APISpec,
  ChatSession,
  ChatMessage,
  LoginForm,
  RegisterForm,
  APISpecForm,
  ChatSessionForm,
  LLMRequest,
  LLMResponse,
  SearchRequest,
  SearchResult,
  FileUploadResponse,
  ApiResponse,
  PaginatedResponse,
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        
        const message = error.response?.data?.detail || error.message || 'An error occurred';
        toast.error(message);
        
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginForm): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response: AxiosResponse<{ access_token: string; token_type: string }> = 
      await this.api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

    return response.data;
  }

  async register(userData: RegisterForm): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/auth/register', userData);
    return response.data;
  }

  // User management
  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/users/me');
    return response.data;
  }

  async updateUser(userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.api.put('/users/me', userData);
    return response.data;
  }

  // API Specifications
  async createAPISpec(specData: APISpecForm): Promise<APISpec> {
    const response: AxiosResponse<APISpec> = await this.api.post('/api-specs', specData);
    return response.data;
  }

  async getAPISpecs(params?: {
    skip?: number;
    limit?: number;
    seal_id?: string;
    application?: string;
  }): Promise<APISpec[]> {
    const response: AxiosResponse<APISpec[]> = await this.api.get('/api-specs', { params });
    return response.data;
  }

  async getAPISpec(specId: number): Promise<APISpec> {
    const response: AxiosResponse<APISpec> = await this.api.get(`/api-specs/${specId}`);
    return response.data;
  }

  async updateAPISpec(specId: number, specData: Partial<APISpecForm>): Promise<APISpec> {
    const response: AxiosResponse<APISpec> = await this.api.put(`/api-specs/${specId}`, specData);
    return response.data;
  }

  async deleteAPISpec(specId: number): Promise<void> {
    await this.api.delete(`/api-specs/${specId}`);
  }

  async uploadFile(file: File, sealId: string, application: string): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('seal_id', sealId);
    formData.append('application', application);

    const response: AxiosResponse<FileUploadResponse> = await this.api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Chat
  async createChatSession(sessionData: ChatSessionForm): Promise<ChatSession> {
    const response: AxiosResponse<ChatSession> = await this.api.post('/chat/sessions', sessionData);
    return response.data;
  }

  async getChatSessions(params?: { skip?: number; limit?: number }): Promise<ChatSession[]> {
    const response: AxiosResponse<ChatSession[]> = await this.api.get('/chat/sessions', { params });
    return response.data;
  }

  async getChatSession(sessionId: number): Promise<ChatSession> {
    const response: AxiosResponse<ChatSession> = await this.api.get(`/chat/sessions/${sessionId}`);
    return response.data;
  }

  async sendMessage(
    sessionId: number,
    message: string,
    includeChainOfThought: boolean = true
  ): Promise<ChatMessage> {
    const response: AxiosResponse<ChatMessage> = await this.api.post(
      `/chat/sessions/${sessionId}/messages`,
      null,
      {
        params: {
          message,
          include_chain_of_thought: includeChainOfThought,
        },
      }
    );
    return response.data;
  }

  async getChatMessages(sessionId: number, limit?: number): Promise<ChatMessage[]> {
    const response: AxiosResponse<ChatMessage[]> = await this.api.get(
      `/chat/sessions/${sessionId}/messages`,
      { params: { limit } }
    );
    return response.data;
  }

  async getChatHistory(sessionId: number): Promise<{
    session: ChatSession;
    messages: ChatMessage[];
  }> {
    const response: AxiosResponse<{
      session: ChatSession;
      messages: ChatMessage[];
    }> = await this.api.get(`/chat/sessions/${sessionId}/history`);
    return response.data;
  }

  // Search
  async searchAPI(query: string, apiSpecIds?: number[], limit?: number): Promise<SearchResult[]> {
    const searchRequest: SearchRequest = {
      query,
      api_spec_ids: apiSpecIds,
      limit: limit || 10,
    };

    const response: AxiosResponse<SearchResult[]> = await this.api.post('/search', searchRequest);
    return response.data;
  }

  // LLM
  async generateLLMResponse(request: LLMRequest): Promise<LLMResponse> {
    const response: AxiosResponse<LLMResponse> = await this.api.post('/llm/generate', request);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; app_name: string; version: string }> {
    const response: AxiosResponse<{ status: string; app_name: string; version: string }> = 
      await this.api.get('/health');
    return response.data;
  }
}

// Create singleton instance
const apiService = new ApiService();
export default apiService;
