import React from 'react';
import { ChatMessage as ChatMessageType } from '../types/chat';
import { 
  UserIcon, 
  CpuChipIcon, 
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.type === 'user';
  const hasMetadata = message.metadata && Object.keys(message.metadata).length > 0;

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMetadata = () => {
    if (!hasMetadata || !message.metadata) return null;

    const { metadata } = message;
    
    return (
      <div className="mt-4 space-y-4">
        {/* Summary Section */}
        {metadata.summary && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
              <CheckCircleIcon className="w-5 h-5 mr-2" />
              Quick Summary
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="text-center">
                <div className="font-semibold text-blue-700">{metadata.summary.apis_identified}</div>
                <div className="text-blue-600">APIs Found</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-blue-700">{metadata.summary.estimated_timeline}</div>
                <div className="text-blue-600">Timeline</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-blue-700">{metadata.summary.estimated_cost}</div>
                <div className="text-blue-600">Cost</div>
              </div>
              <div className="text-center">
                <div className={`font-semibold ${metadata.summary.performance_critical ? 'text-orange-600' : 'text-green-600'}`}>
                  {metadata.summary.performance_critical ? 'Critical' : 'Standard'}
                </div>
                <div className="text-blue-600">Performance</div>
              </div>
            </div>
          </div>
        )}

        {/* API Discovery Section */}
        {metadata.api_discovery && metadata.api_discovery.length > 0 && (
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <h4 className="font-semibold text-green-900 mb-3 flex items-center">
              <CpuChipIcon className="w-5 h-5 mr-2" />
              API Discovery Results
            </h4>
            <div className="space-y-3">
              {metadata.api_discovery.map((api, index) => (
                <div key={index} className="bg-white rounded-lg p-3 border border-green-200">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-semibold text-green-800">{api.api_name}</h5>
                    <div className="flex space-x-2">
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        {Math.round(api.relevance_score * 100)}% relevance
                      </span>
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                        {Math.round(api.performance_score * 100)}% performance
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-green-700 mb-2">
                    <span className="font-medium">Service:</span> {api.service} | <span className="font-medium">System:</span> {api.system}
                  </p>
                  <div className="space-y-1">
                    {api.endpoints.map((endpoint, epIndex) => (
                      <div key={epIndex} className="text-xs bg-gray-100 rounded px-2 py-1 font-mono">
                        <span className="font-semibold">{endpoint.method}</span> {endpoint.path}
                        <span className="text-gray-500 ml-2">- {endpoint.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Onboarding Requirements Section */}
        {metadata.onboarding_requirements && metadata.onboarding_requirements.length > 0 && (
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <h4 className="font-semibold text-purple-900 mb-3 flex items-center">
              <InformationCircleIcon className="w-5 h-5 mr-2" />
              Onboarding Requirements
            </h4>
            <div className="space-y-3">
              {metadata.onboarding_requirements.map((req, index) => (
                <div key={index} className="bg-white rounded-lg p-3 border border-purple-200">
                  <h5 className="font-semibold text-purple-800 mb-2">{req.service_name}</h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="font-medium text-purple-700">Scopes:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {req.required_scopes.map((scope, scopeIndex) => (
                          <span key={scopeIndex} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                            {scope}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="font-medium text-purple-700">Timeline:</span>
                      <div className="text-purple-600 mt-1">{req.estimated_timeline}</div>
                    </div>
                    <div>
                      <span className="font-medium text-purple-700">Auth:</span>
                      <div className="text-purple-600 mt-1">{req.authentication}</div>
                    </div>
                    <div>
                      <span className="font-medium text-purple-700">Approval:</span>
                      <div className="text-purple-600 mt-1">
                        {req.approval_required ? 'Required' : 'Not Required'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Steps Section */}
        {metadata.next_steps && metadata.next_steps.length > 0 && (
          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
              <ExclamationTriangleIcon className="w-5 h-5 mr-2" />
              Actionable Next Steps
            </h4>
            <div className="space-y-2">
              {metadata.next_steps.map((step, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className={`flex-shrink-0 w-3 h-3 rounded-full mt-2 ${
                    step.priority === 'High' ? 'bg-red-500' :
                    step.priority === 'Medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`} />
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <span className="font-medium text-orange-800">{step.action}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        step.priority === 'High' ? 'bg-red-100 text-red-700' :
                        step.priority === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
                      }`}>
                        {step.priority}
                      </span>
                    </div>
                    <div className="text-sm text-orange-700">
                      <span className="font-medium">Owner:</span> {step.owner} | <span className="font-medium">Timeline:</span> {step.timeline}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 animate-slide-up`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-4xl`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-primary-600 text-white' 
            : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
        }`}>
          {isUser ? (
            <UserIcon className="w-6 h-6" />
          ) : (
            <CpuChipIcon className="w-6 h-6" />
          )}
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block rounded-2xl px-4 py-3 ${
            isUser 
              ? 'bg-primary-600 text-white' 
              : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
          }`}>
            {/* Message Header */}
            <div className={`flex items-center space-x-2 mb-2 ${
              isUser ? 'text-primary-100' : 'text-gray-500'
            }`}>
              <span className="text-sm font-medium">
                {isUser ? 'You' : 'CatalystAI'}
              </span>
              <ClockIcon className="w-4 h-4" />
              <span className="text-xs">
                {formatTimestamp(message.timestamp)}
              </span>
            </div>

            {/* Message Text */}
            <div className={`prose prose-sm max-w-none ${
              isUser ? 'text-white' : 'text-gray-900'
            }`}>
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
          </div>

          {/* Metadata Display */}
          {!isUser && hasMetadata && renderMetadata()}
        </div>
      </div>
    </div>
  );
};
