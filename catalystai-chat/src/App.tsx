import React, { useState } from 'react';
import { ChatProvider } from './contexts/ChatContext';
import { ChatInterface } from './components/ChatInterface';
import ApiSpecManagement from './components/ApiSpecManagement';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'api-spec'>('chat');

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
}

export default App;
