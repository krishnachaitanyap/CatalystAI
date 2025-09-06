import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, MicrophoneIcon } from '@heroicons/react/24/outline';
import { sampleQuestions } from '../data/sampleData';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
      setShowSuggestions(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion);
    setShowSuggestions(false);
    textareaRef.current?.focus();
  };

  const toggleSuggestions = () => {
    setShowSuggestions(!showSuggestions);
  };

  return (
    <div className="relative">
      {/* Sample Questions Suggestions */}
      {showSuggestions && (
        <div className="absolute bottom-full mb-4 left-0 right-0 bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-h-64 overflow-y-auto">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-semibold text-gray-700">Sample Questions</h3>
            <button
              onClick={toggleSuggestions}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {sampleQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(question)}
                className="text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded-md transition-colors duration-200 hover:text-primary-600"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-end space-x-3 bg-white rounded-xl border border-gray-200 shadow-sm p-3 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200 transition-all duration-200">
          {/* Textarea */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about API discovery, integration, performance, or any other development questions..."
              className="w-full resize-none border-0 focus:ring-0 focus:outline-none text-gray-900 placeholder-gray-500 text-sm leading-6 max-h-32 overflow-y-auto"
              rows={1}
              disabled={isLoading}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {/* Suggestions Toggle */}
            <button
              type="button"
              onClick={toggleSuggestions}
              className={`p-2 rounded-lg transition-colors duration-200 ${
                showSuggestions 
                  ? 'bg-primary-100 text-primary-600' 
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              }`}
              title="Show sample questions"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>

            {/* Voice Input (Placeholder) */}
            <button
              type="button"
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Voice input (coming soon)"
            >
              <MicrophoneIcon className="w-5 h-5" />
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className={`p-2 rounded-lg transition-all duration-200 ${
                message.trim() && !isLoading
                  ? 'bg-primary-600 text-white hover:bg-primary-700 hover:scale-105'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
              title="Send message"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Character Count */}
        {message.length > 0 && (
          <div className="mt-2 text-xs text-gray-500 text-right">
            {message.length} characters
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="mt-3 text-center">
            <div className="inline-flex items-center space-x-2 text-sm text-gray-500">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
              <span>CatalystAI is analyzing your request...</span>
            </div>
          </div>
        )}
      </form>

      {/* Quick Actions */}
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={() => handleSuggestionClick("I need to integrate with payment APIs for e-commerce. What are my options?")}
          className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full hover:bg-blue-200 transition-colors duration-200"
        >
          💳 Payment APIs
        </button>
        <button
          onClick={() => handleSuggestionClick("How do I implement user authentication with OAuth 2.0?")}
          className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full hover:bg-green-200 transition-colors duration-200"
        >
          🔐 OAuth 2.0
        </button>
        <button
          onClick={() => handleSuggestionClick("I'm building a data analytics dashboard. Which APIs should I use?")}
          className="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full hover:bg-purple-200 transition-colors duration-200"
        >
          📊 Analytics APIs
        </button>
        <button
          onClick={() => handleSuggestionClick("I need to scale my service to handle 10,000 concurrent users. What changes are needed?")}
          className="text-xs bg-orange-100 text-orange-700 px-3 py-1 rounded-full hover:bg-orange-200 transition-colors duration-200"
        >
          ⚡ Scaling
        </button>
      </div>
    </div>
  );
};

