// mushi-frontend/src/views/MushiAiView.jsx
import React from 'react';
import ProviderSelector from '../components/llm/ProviderSelector';
import ChatWindow from '../components/chat/ChatWindow';

function MushiAiView() {
  return (
    <div className="container mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">

        {/* Left Sidebar for Settings */}
        <div className="md:col-span-1">
          <h2 className="text-lg font-semibold mb-4 text-white">Settings</h2>
          <ProviderSelector />
          {/* You can add more settings components here later */}
        </div>

        {/* Main Chat Area */}
        <div className="md:col-span-3">
          <ChatWindow />
        </div>

      </div>
    </div>
  );
}

export default MushiAiView;
