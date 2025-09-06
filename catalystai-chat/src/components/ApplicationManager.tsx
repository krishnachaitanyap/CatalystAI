import React, { useState } from 'react';

interface Application {
  id: string;
  name: string;
  description: string;
  sealId: string;
  createdAt: string;
  updatedAt: string;
  apiCount: number;
}

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

interface ApplicationManagerProps {
  applications: Application[];
  apiSpecs: ApiSpec[];
  onApplicationSelect: (application: Application) => void;
  onApiSpecSelect: (apiSpec: ApiSpec) => void;
}

const ApplicationManager: React.FC<ApplicationManagerProps> = ({
  applications,
  apiSpecs,
  onApplicationSelect,
  onApiSpecSelect
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newApplication, setNewApplication] = useState({
    name: '',
    description: '',
    sealId: '105961' // Default SEALID
  });

  const handleCreateApplication = (e: React.FormEvent) => {
    e.preventDefault();
    if (newApplication.name.trim()) {
      const application: Application = {
        id: `app-${Date.now()}`,
        name: newApplication.name,
        description: newApplication.description,
        sealId: newApplication.sealId,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        apiCount: 0
      };
      
      // In a real app, this would make an API call
      console.log('Creating application:', application);
      
      setNewApplication({ name: '', description: '', sealId: '105961' });
      setShowCreateForm(false);
    }
  };

  const getApiSpecsForApplication = (applicationId: string) => {
    return apiSpecs.filter(api => api.applicationId === applicationId);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'Draft': return 'bg-yellow-100 text-yellow-800';
      case 'Archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'REST': return '🌐';
      case 'SOAP': return '🔧';
      case 'Postman': return '📮';
      default: return '📄';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            Applications (SEALID: 105961)
          </h3>
          <p className="text-sm text-gray-600">
            Manage your applications and their API specifications
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          ➕ Create Application
        </button>
      </div>

      {/* Create Application Form */}
      {showCreateForm && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h4 className="text-lg font-medium text-gray-900 mb-4">
            Create New Application
          </h4>
          <form onSubmit={handleCreateApplication} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Application Name *
              </label>
              <input
                type="text"
                value={newApplication.name}
                onChange={(e) => setNewApplication(prev => ({ ...prev, name: e.target.value }))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter application name"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                value={newApplication.description}
                onChange={(e) => setNewApplication(prev => ({ ...prev, description: e.target.value }))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                placeholder="Enter application description"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                SEALID
              </label>
              <input
                type="text"
                value={newApplication.sealId}
                onChange={(e) => setNewApplication(prev => ({ ...prev, sealId: e.target.value }))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter SEALID"
              />
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Create Application
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Applications Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {applications.map((application) => {
          const appApiSpecs = getApiSpecsForApplication(application.id);
          
          return (
            <div
              key={application.id}
              className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900">
                      {application.name}
                    </h4>
                    <p className="mt-1 text-sm text-gray-600">
                      {application.description}
                    </p>
                    <div className="mt-2 flex items-center text-xs text-gray-500">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        SEALID: {application.sealId}
                      </span>
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <div className="text-2xl font-bold text-blue-600">
                      {application.apiCount}
                    </div>
                    <div className="text-xs text-gray-500">APIs</div>
                  </div>
                </div>
                
                <div className="mt-4 flex items-center justify-between">
                  <div className="text-xs text-gray-500">
                    Updated {new Date(application.updatedAt).toLocaleDateString()}
                  </div>
                  <button
                    onClick={() => onApplicationSelect(application)}
                    className="px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Manage APIs
                  </button>
                </div>
              </div>
              
              {/* API Specs List */}
              {appApiSpecs.length > 0 && (
                <div className="border-t bg-gray-50 px-6 py-4">
                  <h5 className="text-sm font-medium text-gray-900 mb-2">
                    API Specifications
                  </h5>
                  <div className="space-y-2">
                    {appApiSpecs.slice(0, 3).map((apiSpec) => (
                      <div
                        key={apiSpec.id}
                        className="flex items-center justify-between p-2 bg-white rounded border cursor-pointer hover:bg-gray-50"
                        onClick={() => onApiSpecSelect(apiSpec)}
                      >
                        <div className="flex items-center space-x-2">
                          <span className="text-sm">{getTypeIcon(apiSpec.type)}</span>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {apiSpec.name}
                            </div>
                            <div className="text-xs text-gray-500">
                              {apiSpec.format} {apiSpec.version}
                            </div>
                          </div>
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(apiSpec.status)}`}>
                          {apiSpec.status}
                        </span>
                      </div>
                    ))}
                    {appApiSpecs.length > 3 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{appApiSpecs.length - 3} more APIs
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {applications.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📱</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No applications yet
          </h3>
          <p className="text-gray-600 mb-4">
            Create your first application to start managing API specifications
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Create Application
          </button>
        </div>
      )}
    </div>
  );
};

export default ApplicationManager;
