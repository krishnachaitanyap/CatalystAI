export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  query_analysis?: QueryAnalysis;
  api_discovery?: APIDiscoveryResult[];
  onboarding_requirements?: OnboardingRequirement[];
  integration_recommendations?: IntegrationRecommendation[];
  performance_analysis?: PerformanceAnalysis;
  downstream_impact?: DownstreamImpact;
  next_steps?: NextStep[];
  summary?: ResponseSummary;
}

export interface QueryAnalysis {
  primary_intent: string;
  key_entities: string[];
  search_dimensions: string[];
  business_context: string;
}

export interface APIDiscoveryResult {
  api_name: string;
  service: string;
  system: string;
  endpoints: APIEndpoint[];
  relevance_score: number;
  performance_score: number;
  citations: string[];
}

export interface APIEndpoint {
  method: string;
  path: string;
  description: string;
  supports_vendor_id: boolean;
}

export interface OnboardingRequirement {
  service_name: string;
  required_scopes: string[];
  authentication: string;
  rate_limits: string;
  approval_required: boolean;
  estimated_timeline: string;
  dependencies: string[];
}

export interface IntegrationRecommendation {
  category: string;
  recommendations: string[];
}

export interface PerformanceAnalysis {
  tps_requirement: number;
  performance_critical: boolean;
  scaling_needed: boolean;
  recommendations: string[];
  estimated_costs: CostEstimate;
}

export interface CostEstimate {
  additional_compute: string;
  load_balancers: string;
  database_scaling: string;
  monitoring_tools: string;
}

export interface DownstreamImpact {
  infrastructure_team: string[];
  platform_team: string[];
  security_team: string[];
  data_team: string[];
  estimated_timeline: TimelineEstimate;
}

export interface TimelineEstimate {
  infrastructure_scaling: string;
  security_review: string;
  performance_testing: string;
  total_implementation: string;
}

export interface NextStep {
  priority: 'High' | 'Medium' | 'Low';
  action: string;
  owner: string;
  timeline: string;
}

export interface ResponseSummary {
  apis_identified: number;
  scaling_required: boolean;
  performance_critical: boolean;
  estimated_timeline: string;
  estimated_cost: string;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

export interface ChatContextType {
  state: ChatState;
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  isLoading: boolean;
}

