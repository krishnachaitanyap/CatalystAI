// API Types
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface APISpec {
  id: number;
  name: string;
  description?: string;
  api_type: 'REST' | 'SOAP';
  spec_type?: 'REST' | 'SOAP';
  format: string;
  seal_id: string;
  application: string;
  version: string;
  base_url?: string;
  spec_content: string;
  file_name?: string;
  status?: 'active' | 'error' | 'warning' | 'pending';
  metadata?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  owner_id: number;
}

export interface ChatSession {
  id: number;
  title?: string;
  context?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user_id: number;
  api_spec_id?: number;
  messages: ChatMessage[];
}

export interface ChatMessage {
  id: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  message_type: 'text' | 'markdown' | 'widget';
  metadata?: Record<string, any>;
  chain_of_thought?: string;
  tokens_used: number;
  created_at: string;
  session_id: number;
}

export interface LLMRequest {
  message: string;
  context?: Record<string, any>;
  include_chain_of_thought: boolean;
  max_tokens?: number;
  temperature?: number;
}

export interface LLMResponse {
  response: string;
  chain_of_thought?: string;
  tokens_used: number;
  model_used: string;
}

export interface SearchRequest {
  query: string;
  api_spec_ids?: number[];
  limit: number;
}

export interface SearchResult {
  content: string;
  metadata: Record<string, any>;
  score: number;
  api_spec_id: number;
}

export interface FileUploadResponse {
  filename: string;
  file_type: string;
  size: number;
  message: string;
}

// Form Types
export interface LoginForm {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
}

export interface APISpecForm {
  name: string;
  description?: string;
  api_type: 'REST' | 'SOAP';
  format: string;
  seal_id: string;
  application: string;
  version: string;
  base_url?: string;
  spec_content: string;
  metadata?: Record<string, any>;
}

export interface ChatSessionForm {
  title?: string;
  context?: Record<string, any>;
  api_spec_id?: number;
}

// UI Types
export interface WidgetProps {
  type: 'chart' | 'button' | 'table' | 'code' | 'json';
  data: any;
  config?: Record<string, any>;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string[];
    borderColor?: string;
  }[];
}

export interface TableData {
  columns: string[];
  rows: (string | number)[][];
}

// Store Types
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginForm) => Promise<void>;
  register: (userData: RegisterForm) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => Promise<void>;
}

export interface ChatState {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  createSession: (data: ChatSessionForm) => Promise<ChatSession>;
  loadSession: (sessionId: number) => Promise<void>;
  sendMessage: (sessionId: number, message: string, includeChainOfThought?: boolean) => Promise<void>;
  loadSessions: () => Promise<void>;
  loadMessages: (sessionId: number) => Promise<void>;
  deleteSession: (sessionId: number) => Promise<void>;
}

export interface APISpecState {
  specs: APISpec[];
  currentSpec: APISpec | null;
  isLoading: boolean;
  error: string | null;
  createSpec: (data: APISpecForm) => Promise<APISpec>;
  loadSpecs: () => Promise<void>;
  loadSpec: (specId: number) => Promise<void>;
  updateSpec: (specId: number, data: Partial<APISpecForm>) => Promise<void>;
  deleteSpec: (specId: number) => Promise<void>;
  uploadFile: (file: File, sealId: string, application: string) => Promise<FileUploadResponse>;
}

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}

// Error Types
export interface ApiError {
  detail: string;
  status_code: number;
}

// Configuration Types
export interface AppConfig {
  apiBaseUrl: string;
  chunkingStrategy: 'FIXED_SIZE' | 'SEMANTIC' | 'HYBRID' | 'ENDPOINT_BASED';
  chunkSize: number;
  chunkOverlap: number;
  llmModel: string;
  llmTemperature: number;
  llmMaxTokens: number;
}
