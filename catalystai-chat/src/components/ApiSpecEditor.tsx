import React, { useState, useEffect } from 'react';
import AttributeHierarchyView from './AttributeHierarchyView';
import { APISpec } from '../services/dataCollectorAPI';

interface CommonAPISpec {
  api_name: string;
  version: string;
  description: string;
  base_url: string;
  category: string;
  documentation_url: string;
  api_type: 'REST' | 'SOAP';
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
  // REST fields
  path?: string;
  method: string;
  summary?: string;
  description?: string;
  parameters?: Parameter[];
  request_body?: RequestBody;
  responses?: { [key: string]: Response };
  tags?: string[];
  operation_id?: string;
  deprecated?: boolean;
  
  // SOAP fields
  operation_name?: string;
  soap_action?: string;
  soap_headers?: SoapHeader[];
  input_message?: SoapMessage;
  output_message?: SoapMessage;
}

interface Parameter {
  name: string;
  in: string;
  description?: string;
  required?: boolean;
  type?: string;
  schema?: any;
}

interface RequestBody {
  description?: string;
  required?: boolean;
  content_type?: string;
  soap_envelope?: boolean;
  parts?: SoapPart[];
}

interface Response {
  description?: string;
  content_type?: string;
  soap_envelope?: boolean;
  parts?: SoapPart[];
}

interface SoapHeader {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
}

interface SoapMessage {
  all_attributes: Attribute[];
}

interface SoapPart {
  name: string;
  element?: string;
  type?: string;
  schema_details?: any;
  attributes?: Attribute[];
}

interface Attribute {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  min_occurs?: string;
  max_occurs?: string;
  nillable?: boolean;
  parent_path?: string;
  is_nested?: boolean;
  properties?: Attribute[];
}

interface Authentication {
  type: string;
  schemes: any[];
}

interface RateLimits {
  description: string;
}

interface ContactInfo {
  [key: string]: any;
}

interface LicenseInfo {
  [key: string]: any;
}

interface ApiSpecEditorProps {
  apiSpec: APISpec;
  onSave: () => void;
}

const ApiSpecEditor: React.FC<ApiSpecEditorProps> = ({
  apiSpec,
  onSave
}) => {
  const [commonSpec, setCommonSpec] = useState<CommonAPISpec | null>(null);
  const [activeTab, setActiveTab] = useState<'basic' | 'endpoints' | 'auth' | 'advanced'>('basic');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Load CommonAPISpec data from apiSpec.common_spec_data
  useEffect(() => {
    const loadCommonSpec = async () => {
      setIsLoading(true);
      
      // Use real CommonAPISpec data from the API spec
      if (apiSpec.common_spec_data) {
        setCommonSpec(apiSpec.common_spec_data as CommonAPISpec);
      } else {
        // Fallback to basic data if no common_spec_data available
        const fallbackSpec: CommonAPISpec = {
          api_name: apiSpec.name,
          version: apiSpec.version,
          description: apiSpec.description || '',
          base_url: apiSpec.base_url || '',
          category: apiSpec.api_type === 'SOAP' ? 'soap' : 'rest',
          documentation_url: '',
          api_type: apiSpec.api_type === 'SOAP' ? 'SOAP' : 'REST',
          endpoints: [],
          authentication: { type: 'none', schemes: [] },
          rate_limits: { description: 'Not specified' },
          pricing: null,
          sdk_languages: [],
          integration_steps: [],
          best_practices: [],
          common_use_cases: [],
          tags: [apiSpec.api_type.toLowerCase()],
          contact_info: {},
          license_info: {},
          external_docs: [],
          examples: [],
          schema_version: '1.0',
          created_at: apiSpec.created_at,
          updated_at: apiSpec.updated_at
        };
        setCommonSpec(fallbackSpec);
      }
      
      setIsLoading(false);
    };
    
    loadCommonSpec();
  }, [apiSpec]);

  const handleSave = async () => {
    if (!commonSpec) return;
    
    setIsSaving(true);
    
    try {
      // TODO: Implement save logic
      await new Promise(resolve => setTimeout(resolve, 1000));
      onSave();
    } catch (error) {
      console.error('Failed to save API spec:', error);
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
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading API specification...</span>
      </div>
    );
  }

  if (!commonSpec) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-500">No API specification data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            {commonSpec.api_name} v{commonSpec.version}
          </h3>
          <p className="text-sm text-gray-500">
            {commonSpec.api_type} • {apiSpec.format}
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'basic', label: 'Basic Info' },
            { id: 'endpoints', label: 'Endpoints' },
            { id: 'auth', label: 'Authentication' },
            { id: 'advanced', label: 'Advanced' }
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
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'basic' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                API Name
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
                Version
              </label>
              <input
                type="text"
                value={commonSpec.version}
                onChange={(e) => updateCommonSpec({ version: e.target.value })}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                value={commonSpec.description}
                onChange={(e) => updateCommonSpec({ description: e.target.value })}
                rows={3}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Base URL
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
        </div>
      )}

      {activeTab === 'endpoints' && (
        <div className="space-y-6">
          <h4 className="text-lg font-medium text-gray-900">Endpoints</h4>
          
          {commonSpec.endpoints.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No endpoints available. This might be because the API specification hasn't been fully processed yet.
            </div>
          ) : (
            <div className="space-y-4">
              {commonSpec.endpoints.map((endpoint, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                        {endpoint.method}
                      </span>
                      <span className="font-medium text-gray-900">
                        {endpoint.path || endpoint.operation_name}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {endpoint.operation_id || endpoint.soap_action}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    {endpoint.description || endpoint.summary}
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    {endpoint.parameters?.length || 0} parameters • {Object.keys(endpoint.responses || {}).length} responses
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'auth' && (
        <div className="space-y-6">
          <h4 className="text-lg font-medium text-gray-900">Authentication</h4>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">
              Authentication type: <span className="font-medium">{commonSpec.authentication.type}</span>
            </p>
            {commonSpec.authentication.schemes.length > 0 && (
              <div className="mt-2">
                <p className="text-sm text-gray-600">Available schemes:</p>
                <ul className="list-disc list-inside mt-1 text-sm text-gray-500">
                  {commonSpec.authentication.schemes.map((scheme, index) => (
                    <li key={index}>{scheme.name || scheme.type}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'advanced' && (
        <div className="space-y-6">
          <h4 className="text-lg font-medium text-gray-900">Advanced Settings</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                SDK Languages
              </label>
              <input
                type="text"
                value={commonSpec.sdk_languages.join(', ')}
                onChange={(e) => updateCommonSpec({ sdk_languages: e.target.value.split(', ').filter(l => l.trim()) })}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Java, Python, C#, JavaScript"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Tags
              </label>
              <input
                type="text"
                value={commonSpec.tags.join(', ')}
                onChange={(e) => updateCommonSpec({ tags: e.target.value.split(', ').filter(t => t.trim()) })}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="api, rest, soap"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Integration Steps
            </label>
            <textarea
              value={commonSpec.integration_steps.join('\n')}
              onChange={(e) => updateCommonSpec({ integration_steps: e.target.value.split('\n').filter(s => s.trim()) })}
              rows={4}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Step 1: Obtain API credentials&#10;Step 2: Configure authentication&#10;Step 3: Test API endpoints"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Best Practices
            </label>
            <textarea
              value={commonSpec.best_practices.join('\n')}
              onChange={(e) => updateCommonSpec({ best_practices: e.target.value.split('\n').filter(p => p.trim()) })}
              rows={4}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Use HTTPS for all API calls&#10;Implement proper error handling&#10;Cache responses when appropriate"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiSpecEditor;