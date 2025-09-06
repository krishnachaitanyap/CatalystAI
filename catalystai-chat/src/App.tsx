import React from 'react';
import { ChatProvider } from './contexts/ChatContext';
import { ChatInterface } from './components/ChatInterface';

function App() {
  return (
    <ChatProvider>
      <ChatInterface />
    </ChatProvider>
  );
}

export default App;
