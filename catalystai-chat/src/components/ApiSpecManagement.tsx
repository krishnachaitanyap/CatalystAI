import React, { useState, useEffect } from 'react';
import ApplicationManager from './ApplicationManager';
import ApiUploader from './ApiUploader';
import ApiSpecEditor from './ApiSpecEditor';

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

const ApiSpecManagement: React.FC = () => {
  const [activeView, setActiveView] = useState<'applications' | 'upload' | 'editor'>('applications');
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);
  const [selectedApiSpec, setSelectedApiSpec] = useState<ApiSpec | null>(null);
  const [apiSpecs, setApiSpecs] = useState<ApiSpec[]>([]);

  // Load sample data on component mount
  useEffect(() => {
    loadSampleData();
  }, []);

  const loadSampleData = () => {
    // Sample applications
    const sampleApplications: Application[] = [
      {
        id: 'app-1',
        name: 'E-Commerce Platform',
        description: 'Main e-commerce application for online retail',
        sealId: '105961',
        createdAt: '2024-01-15T10:00:00Z',
        updatedAt: '2024-09-06T15:30:00Z',
        apiCount: 12
      },
      {
        id: 'app-2',
        name: 'Customer Management System',
        description: 'CRM system for customer relationship management',
        sealId: '105961',
        createdAt: '2024-02-20T14:00:00Z',
        updatedAt: '2024-09-05T09:15:00Z',
        apiCount: 8
      },
      {
        id: 'app-3',
        name: 'Payment Gateway Service',
        description: 'Payment processing and gateway services',
        sealId: '105961',
        createdAt: '2024-03-10T11:30:00Z',
        updatedAt: '2024-09-04T16:45:00Z',
        apiCount: 5
      }
    ];

    // Sample API specs
    const sampleApiSpecs: ApiSpec[] = [
      {
        id: 'api-1',
        applicationId: 'app-1',
        name: 'Product Catalog API',
        type: 'REST',
        format: 'OpenAPI',
        version: '3.0.1',
        description: 'API for managing product catalog operations',
        baseUrl: 'https://api.ecommerce.com/v1',
        status: 'Active',
        createdAt: '2024-01-20T10:00:00Z',
        updatedAt: '2024-09-06T15:30:00Z'
      },
      {
        id: 'api-2',
        applicationId: 'app-1',
        name: 'Order Management API',
        type: 'REST',
        format: 'Swagger',
        version: '2.0',
        description: 'API for order processing and management',
        baseUrl: 'https://api.ecommerce.com/v2',
        status: 'Active',
        createdAt: '2024-01-25T14:00:00Z',
        updatedAt: '2024-09-05T09:15:00Z'
      },
      {
        id: 'api-3',
        applicationId: 'app-2',
        name: 'Customer Service API',
        type: 'SOAP',
        format: 'WSDL',
        version: '1.1',
        description: 'SOAP service for customer management operations',
        baseUrl: 'https://services.crm.com/customer',
        status: 'Active',
        createdAt: '2024-02-25T11:30:00Z',
        updatedAt: '2024-09-04T16:45:00Z'
      }
    ];

    setApplications(sampleApplications);
    setApiSpecs(sampleApiSpecs);
  };

  const handleApplicationSelect = (application: Application) => {
    setSelectedApplication(application);
    setActiveView('upload');
  };

  const handleApiSpecSelect = (apiSpec: ApiSpec) => {
    setSelectedApiSpec(apiSpec);
    setActiveView('editor');
  };

  const handleBackToApplications = () => {
    setSelectedApplication(null);
    setSelectedApiSpec(null);
    setActiveView('applications');
  };

  const handleBackToUpload = () => {
    setSelectedApiSpec(null);
    setActiveView('upload');
  };

  const handleApiUploaded = (newApiSpec: ApiSpec) => {
    setApiSpecs(prev => [...prev, newApiSpec]);
    setActiveView('applications');
    setSelectedApplication(null);
  };

  const handleApiSpecUpdated = (updatedApiSpec: ApiSpec) => {
    setApiSpecs(prev => prev.map(api => 
      api.id === updatedApiSpec.id ? updatedApiSpec : api
    ));
    setActiveView('applications');
    setSelectedApplication(null);
    setSelectedApiSpec(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">
            📋 API Specification Management
          </h2>
          <p className="mt-2 text-gray-600">
            Manage applications and their API specifications for enterprise integration
          </p>
        </div>
        
        {activeView !== 'applications' && (
          <div className="flex space-x-3">
            {activeView === 'editor' && (
              <button
                onClick={handleBackToUpload}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                ← Back to Upload
              </button>
            )}
            <button
              onClick={handleBackToApplications}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              ← Back to Applications
            </button>
          </div>
        )}
      </div>

      {/* Content based on active view */}
      {activeView === 'applications' && (
        <ApplicationManager
          applications={applications}
          apiSpecs={apiSpecs}
          onApplicationSelect={handleApplicationSelect}
          onApiSpecSelect={handleApiSpecSelect}
        />
      )}

      {activeView === 'upload' && selectedApplication && (
        <ApiUploader
          application={selectedApplication}
          onApiUploaded={handleApiUploaded}
          onBack={handleBackToApplications}
        />
      )}

      {activeView === 'editor' && selectedApiSpec && (
        <ApiSpecEditor
          apiSpec={selectedApiSpec}
          onApiSpecUpdated={handleApiSpecUpdated}
          onBack={handleBackToUpload}
        />
      )}
    </div>
  );
};

export default ApiSpecManagement;
