import React, { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useChat } from '../contexts/ChatContext';
import { 
  TrashIcon, 
  ArrowDownIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline';

export const ChatInterface: React.FC = () => {
  const { state, sendMessage, clearChat, isLoading } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = React.useState(false);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages]);

  // Show scroll button when not at bottom
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
    setShowScrollButton(!isAtBottom);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat? This action cannot be undone.')) {
      clearChat();
    }
  };

  return (
    <div className="space-y-6">
      {/* Chat Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            💬 Chat Interface
          </h3>
          <p className="text-sm text-gray-600">
            Ask questions about API discovery, integration, and best practices
          </p>
        </div>
        <button
          onClick={handleClearChat}
          className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          title="Clear chat"
        >
          <TrashIcon className="w-4 h-4" />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Chat Container */}
      <div className="bg-white rounded-lg shadow-sm border">
        {/* Chat Messages */}
        <div className="h-96 overflow-y-auto px-6 py-4 space-y-4" onScroll={handleScroll}>
        {state.messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <SparklesIcon className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Welcome to CatalystAI</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Ask me about API discovery, integration best practices, performance optimization, 
              or any other development questions. I'll provide comprehensive, actionable insights.
            </p>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Try asking:</p>
              <div className="flex flex-wrap justify-center gap-2">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                  "I need payment APIs for e-commerce"
                </span>
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                  "How to implement OAuth 2.0?"
                </span>
                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                  "Which analytics APIs should I use?"
                </span>
              </div>
            </div>
          </div>
        ) : (
          state.messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        
          {/* Scroll to bottom anchor */}
          <div ref={messagesEndRef} />
        </div>

        {/* Scroll to Bottom Button */}
        {showScrollButton && (
          <button
            onClick={scrollToBottom}
            className="absolute bottom-20 right-6 w-10 h-10 bg-white border border-gray-200 rounded-full shadow-lg flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-50 transition-all duration-200 hover:scale-105"
            title="Scroll to bottom"
          >
            <ArrowDownIcon className="w-4 h-4" />
          </button>
        )}

        {/* Error Display */}
        {state.error && (
          <div className="px-6 py-3 bg-red-50 border-t border-red-200">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">!</span>
              </div>
              <span className="text-red-800 font-medium text-sm">Error</span>
            </div>
            <p className="text-red-700 text-sm mt-1">{state.error}</p>
          </div>
        )}

        {/* Chat Input */}
        <div className="border-t border-gray-200 px-6 py-4">
          <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};

