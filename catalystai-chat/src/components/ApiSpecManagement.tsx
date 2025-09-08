import React, { useState } from 'react';
import { useApp } from '../contexts/AuthContext';
import { Application, APISpec } from '../services/dataCollectorAPI';
import ApplicationManager from './ApplicationManager';
import ApiUploader from './ApiUploader';
import ApiSpecEditor from './ApiSpecEditor';

const ApiSpecManagement: React.FC = () => {
  const { selectedApplication, apiSpecs } = useApp();
  const [activeView, setActiveView] = useState<'applications' | 'upload' | 'editor'>('applications');
  const [selectedApiSpec, setSelectedApiSpec] = useState<APISpec | null>(null);

  const handleApplicationSelect = (application: Application) => {
    setActiveView('upload');
  };

  const handleApiSpecSelect = (apiSpec: APISpec) => {
    setSelectedApiSpec(apiSpec);
    setActiveView('editor');
  };

  const handleApiUploaded = (apiSpec: APISpec) => {
    // API spec was uploaded successfully
    setActiveView('applications');
  };

  const handleBackToApplications = () => {
    setActiveView('applications');
    setSelectedApiSpec(null);
  };

  const handleBackToUpload = () => {
    setActiveView('upload');
    setSelectedApiSpec(null);
  };

  return (
    <div className="space-y-6">
      {/* Navigation Breadcrumb */}
      <nav className="flex items-center space-x-2 text-sm text-gray-500">
        <button
          onClick={handleBackToApplications}
          className="hover:text-gray-700 focus:outline-none"
        >
          Applications
        </button>
        {activeView === 'upload' && (
          <>
            <span>›</span>
            <span className="text-gray-700">Upload API Spec</span>
          </>
        )}
        {activeView === 'editor' && (
          <>
            <span>›</span>
            <button
              onClick={handleBackToUpload}
              className="hover:text-gray-700 focus:outline-none"
            >
              Upload API Spec
            </button>
            <span>›</span>
            <span className="text-gray-700">Edit API Spec</span>
          </>
        )}
      </nav>

      {/* Content based on active view */}
      {activeView === 'applications' && (
        <ApplicationManager
          onApplicationSelect={handleApplicationSelect}
          onApiSpecSelect={handleApiSpecSelect}
        />
      )}

      {activeView === 'upload' && selectedApplication && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Upload API Specification
            </h2>
            <p className="text-gray-600 mb-4">
              Upload API specifications for <strong>{selectedApplication.name}</strong>
            </p>
            <ApiUploader
              application={selectedApplication}
              onApiUploaded={handleApiUploaded}
            />
          </div>
        </div>
      )}

      {activeView === 'editor' && selectedApiSpec && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Edit API Specification
            </h2>
            <p className="text-gray-600 mb-4">
              Edit details for <strong>{selectedApiSpec.name}</strong>
            </p>
            <ApiSpecEditor
              apiSpec={selectedApiSpec}
              onSave={() => {
                // Handle save logic here
                console.log('API spec saved');
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiSpecManagement;