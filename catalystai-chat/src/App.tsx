import React, { useState } from 'react';
import { ChatProvider } from './contexts/ChatContext';
import { CombinedProvider, useAuth } from './contexts/AuthContext';
import { ChatInterface } from './components/ChatInterface';
import ApiSpecManagement from './components/ApiSpecManagement';
import LoginForm from './components/LoginForm';
import './App.css';

const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'api-spec'>('chat');
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm />;
  }

  return (
    <div className="App">
      <ChatProvider>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <div className="flex items-center">
                  <h1 className="text-2xl font-bold text-gray-900">
                    🔗 CatalystAI
                  </h1>
                  <span className="ml-3 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                    API Discovery & Integration
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  Powered by AI • Enterprise Ready
                </div>
              </div>
              
              {/* Tab Navigation */}
              <div className="border-t border-gray-200">
                <nav className="-mb-px flex space-x-8">
                  <button
                    onClick={() => setActiveTab('chat')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'chat'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    💬 Chat Interface
                  </button>
                  <button
                    onClick={() => setActiveTab('api-spec')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'api-spec'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    📋 API Spec Management
                  </button>
                </nav>
              </div>
            </div>
          </header>
          
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {activeTab === 'chat' && <ChatInterface />}
            {activeTab === 'api-spec' && <ApiSpecManagement />}
          </main>
        </div>
      </ChatProvider>
    </div>
  );
};

function App() {
  return (
    <CombinedProvider>
      <AppContent />
    </CombinedProvider>
  );
}

export default App;
