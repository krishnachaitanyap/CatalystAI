import React, { useState, useEffect } from 'react';

interface ApiSpec {
  id: string;
  applicationId: string;
  name: string;
  type: 'REST' | 'SOAP' | 'Postman';
  format: 'Swagger' | 'OpenAPI' | 'WSDL' | 'XSD' | 'Postman Collection';
  version: string;
  description: string;
  baseUrl: string;
  status: 'Active' | 'Draft' | 'Archived';
  createdAt: string;
  updatedAt: string;
}

interface CommonAPISpec {
  api_name: string;
  version: string;
  description: string;
  base_url: string;
  category: string;
  documentation_url: string;
  endpoints: Endpoint[];
  authentication: Authentication;
  rate_limits: RateLimits;
  pricing: any;
  sdk_languages: string[];
  integration_steps: string[];
  best_practices: string[];
  common_use_cases: string[];
  tags: string[];
  contact_info: ContactInfo;
  license_info: LicenseInfo;
  external_docs: any[];
  examples: any[];
  schema_version: string;
  created_at: string;
  updated_at: string;
}

interface Endpoint {
  path: string;
  method: string;
  summary: string;
  description: string;
  parameters: Parameter[];
  request_body: RequestBody;
  responses: { [key: string]: Response };
  tags: string[];
  operation_id: string;
  deprecated: boolean;
}

interface Parameter {
  name: string;
  in: string;
  description: string;
  required: boolean;
  type: string;
  format: string;
  schema: any;
  example: string;
  enum: string[];
  default: string;
  minimum: string;
  maximum: string;
  min_length: string;
  max_length: string;
  pattern: string;
}

interface RequestBody {
  description: string;
  required: boolean;
  content: { [key: string]: any };
  all_attributes: any[];
  searchable_content: string;
}

interface Response {
  description: string;
  headers: { [key: string]: any };
  content: { [key: string]: any };
  all_attributes: any[];
  searchable_content: string;
}

interface Authentication {
  type: string;
  schemes: AuthScheme[];
  description: string;
}

interface AuthScheme {
  name: string;
  type: string;
  description: string;
  in: string;
  flow: string;
  authorization_url: string;
  token_url: string;
  scopes: { [key: string]: string };
}

interface RateLimits {
  requests_per_second: number | null;
  requests_per_minute: number | null;
  requests_per_hour: number | null;
  requests_per_day: number | null;
  description: string;
}

interface ContactInfo {
  name: string;
  email: string;
  url: string;
}

interface LicenseInfo {
  name: string;
  url: string;
}

interface ApiSpecEditorProps {
  apiSpec: ApiSpec;
  onApiSpecUpdated: (apiSpec: ApiSpec) => void;
  onBack: () => void;
}

const ApiSpecEditor: React.FC<ApiSpecEditorProps> = ({
  apiSpec,
  onApiSpecUpdated,
  onBack
}) => {
  const [commonSpec, setCommonSpec] = useState<CommonAPISpec | null>(null);
  const [activeTab, setActiveTab] = useState<'basic' | 'endpoints' | 'auth' | 'advanced'>('basic');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Load CommonAPISpec data (simulated)
  useEffect(() => {
    const loadCommonSpec = async () => {
      setIsLoading(true);
      
      // Simulate API call to load CommonAPISpec
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock CommonAPISpec data
      const mockCommonSpec: CommonAPISpec = {
        api_name: apiSpec.name,
        version: apiSpec.version,
        description: apiSpec.description,
        base_url: apiSpec.baseUrl,
        category: 'Enterprise',
        documentation_url: '',
        endpoints: [
          {
            path: '/api/v1/users',
            method: 'GET',
            summary: 'Get users',
            description: 'Retrieve list of users',
            parameters: [
              {
                name: 'limit',
                in: 'query',
                description: 'Number of users to return',
                required: false,
                type: 'integer',
                format: 'int32',
                schema: {},
                example: '10',
                enum: [],
                default: '10',
                minimum: '1',
                maximum: '100',
                min_length: '',
                max_length: '',
                pattern: ''
              }
            ],
            request_body: {
              description: '',
              required: false,
              content: {},
              all_attributes: [],
              searchable_content: ''
            },
            responses: {
              '200': {
                description: 'Successful response',
                headers: {},
                content: {},
                all_attributes: [],
                searchable_content: 'Status: 200 Description: Successful response'
              }
            },
            tags: ['users'],
            operation_id: 'getUsers',
            deprecated: false
          }
        ],
        authentication: {
          type: 'oauth2',
          schemes: [
            {
              name: 'oauth2',
              type: 'oauth2',
              description: 'OAuth 2.0 authentication',
              in: 'header',
              flow: 'implicit',
              authorization_url: 'https://auth.example.com/oauth/authorize',
              token_url: 'https://auth.example.com/oauth/token',
              scopes: {
                'read': 'Read access',
                'write': 'Write access'
              }
            }
          ],
          description: 'OAuth 2.0 authentication required'
        },
        rate_limits: {
          requests_per_second: 100,
          requests_per_minute: 6000,
          requests_per_hour: 360000,
          requests_per_day: 8640000,
          description: 'Rate limits apply per API key'
        },
        pricing: null,
        sdk_languages: ['Python', 'JavaScript', 'Java', 'C#', 'Go'],
        integration_steps: [
          'Register your application',
          'Obtain API credentials',
          'Implement authentication',
          'Make API calls',
          'Handle responses'
        ],
        best_practices: [
          'Use HTTPS in production',
          'Implement proper error handling',
          'Cache responses when appropriate',
          'Monitor API usage'
        ],
        common_use_cases: ['User Management', 'Data Integration'],
        tags: ['api', 'rest', 'enterprise'],
        contact_info: {
          name: 'API Support Team',
          email: 'support@example.com',
          url: 'https://support.example.com'
        },
        license_info: {
          name: 'MIT',
          url: 'https://opensource.org/licenses/MIT'
        },
        external_docs: [],
        examples: [],
        schema_version: '1.0',
        created_at: apiSpec.createdAt,
        updated_at: apiSpec.updatedAt
      };
      
      setCommonSpec(mockCommonSpec);
      setIsLoading(false);
    };

    loadCommonSpec();
  }, [apiSpec]);

  const handleSave = async () => {
    if (!commonSpec) return;
    
    setIsSaving(true);
    
    try {
      // Simulate API call to save changes
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const updatedApiSpec: ApiSpec = {
        ...apiSpec,
        name: commonSpec.api_name,
        version: commonSpec.version,
        description: commonSpec.description,
        baseUrl: commonSpec.base_url,
        updatedAt: new Date().toISOString()
      };
      
      onApiSpecUpdated(updatedApiSpec);
    } catch (error) {
      console.error('Save failed:', error);
      alert('Save failed. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const updateCommonSpec = (updates: Partial<CommonAPISpec>) => {
    if (commonSpec) {
      setCommonSpec({ ...commonSpec, ...updates });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading API specification...</p>
        </div>
      </div>
    );
  }

  if (!commonSpec) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load API specification</p>
        <button
          onClick={onBack}
          className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            Edit API Specification
          </h3>
          <p className="text-sm text-gray-600">
            {apiSpec.name} • {apiSpec.type} • {apiSpec.format}
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'basic', label: 'Basic Info', icon: '📋' },
            { id: 'endpoints', label: 'Endpoints', icon: '🔗' },
            { id: 'auth', label: 'Authentication', icon: '🔐' },
            { id: 'advanced', label: 'Advanced', icon: '⚙️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6">
          {activeTab === 'basic' && (
            <div className="space-y-6">
              <h4 className="text-lg font-medium text-gray-900">Basic Information</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    API Name *
                  </label>
                  <input
                    type="text"
                    value={commonSpec.api_name}
                    onChange={(e) => updateCommonSpec({ api_name: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Version *
                  </label>
                  <input
                    type="text"
                    value={commonSpec.version}
                    onChange={(e) => updateCommonSpec({ version: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Base URL *
                  </label>
                  <input
                    type="url"
                    value={commonSpec.base_url}
                    onChange={(e) => updateCommonSpec({ base_url: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Category
                  </label>
                  <select
                    value={commonSpec.category}
                    onChange={(e) => updateCommonSpec({ category: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Enterprise">Enterprise</option>
                    <option value="Public">Public</option>
                    <option value="Internal">Internal</option>
                    <option value="Partner">Partner</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  value={commonSpec.description}
                  onChange={(e) => updateCommonSpec({ description: e.target.value })}
                  rows={4}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Documentation URL
                </label>
                <input
                  type="url"
                  value={commonSpec.documentation_url}
                  onChange={(e) => updateCommonSpec({ documentation_url: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          )}

          {activeTab === 'endpoints' && (
            <div className="space-y-6">
              <h4 className="text-lg font-medium text-gray-900">Endpoints</h4>
              
              <div className="space-y-4">
                {commonSpec.endpoints.map((endpoint, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                          {endpoint.method}
                        </span>
                        <span className="font-medium text-gray-900">{endpoint.path}</span>
                      </div>
                      <span className="text-sm text-gray-500">{endpoint.operation_id}</span>
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-2">
                      {endpoint.description}
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      {endpoint.parameters.length} parameters • {Object.keys(endpoint.responses).length} responses
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'auth' && (
            <div className="space-y-6">
              <h4 className="text-lg font-medium text-gray-900">Authentication</h4>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Authentication Type
                </label>
                <select
                  value={commonSpec.authentication.type}
                  onChange={(e) => updateCommonSpec({ 
                    authentication: { 
                      ...commonSpec.authentication, 
                      type: e.target.value 
                    } 
                  })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="none">None</option>
                  <option value="apiKey">API Key</option>
                  <option value="oauth2">OAuth 2.0</option>
                  <option value="bearer">Bearer Token</option>
                  <option value="basic">Basic Auth</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Authentication Description
                </label>
                <textarea
                  value={commonSpec.authentication.description}
                  onChange={(e) => updateCommonSpec({ 
                    authentication: { 
                      ...commonSpec.authentication, 
                      description: e.target.value 
                    } 
                  })}
                  rows={3}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          )}

          {activeTab === 'advanced' && (
            <div className="space-y-6">
              <h4 className="text-lg font-medium text-gray-900">Advanced Settings</h4>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  SDK Languages
                </label>
                <div className="mt-2 space-y-2">
                  {['Python', 'JavaScript', 'Java', 'C#', 'Go', 'Ruby', 'PHP', 'Swift', 'Kotlin'].map((lang) => (
                    <label key={lang} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={commonSpec.sdk_languages.includes(lang)}
                        onChange={(e) => {
                          const languages = e.target.checked
                            ? [...commonSpec.sdk_languages, lang]
                            : commonSpec.sdk_languages.filter(l => l !== lang);
                          updateCommonSpec({ sdk_languages: languages });
                        }}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      />
                      <span className="ml-2 text-sm text-gray-700">{lang}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Tags
                </label>
                <input
                  type="text"
                  value={commonSpec.tags.join(', ')}
                  onChange={(e) => updateCommonSpec({ tags: e.target.value.split(',').map(t => t.trim()).filter(t => t) })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="api, rest, enterprise"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Contact Name
                  </label>
                  <input
                    type="text"
                    value={commonSpec.contact_info.name}
                    onChange={(e) => updateCommonSpec({ 
                      contact_info: { 
                        ...commonSpec.contact_info, 
                        name: e.target.value 
                      } 
                    })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Contact Email
                  </label>
                  <input
                    type="email"
                    value={commonSpec.contact_info.email}
                    onChange={(e) => updateCommonSpec({ 
                      contact_info: { 
                        ...commonSpec.contact_info, 
                        email: e.target.value 
                      } 
                    })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApiSpecEditor;
