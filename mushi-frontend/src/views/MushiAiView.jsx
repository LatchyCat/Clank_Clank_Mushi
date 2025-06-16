// src/views/MushiAiView.jsx
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import ProviderSelector from '../components/llm/ProviderSelector';
import ChatWindow from '../components/chat/ChatWindow';

function MushiAiView() {
  const location = useLocation();
  const initialQueryFromState = location.state?.preloadedQuery;
  const [initialQuery, setInitialQuery] = useState(initialQueryFromState);

  useEffect(() => {
    if (initialQuery) {
      const timer = setTimeout(() => setInitialQuery(null), 1);
      return () => clearTimeout(timer);
    }
  }, [initialQuery]);

  // The component now assumes it's being rendered within the AppLayout, which provides the background and base padding.
  return (
    // We add a container to constrain the content width, similar to other views.
    <div className="container mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar for settings */}
        <aside className="lg:col-span-1 p-6 bg-background/50 backdrop-blur-md rounded-2xl shadow-lg border border-border self-start">
          <h2 className="text-xl font-bold mb-4 text-center bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400 drop-shadow-lg">
            Mushi AI Settings
          </h2>
          <ProviderSelector />
          {/* You could add more settings here in the future */}
          <div className="mt-6 text-xs text-muted-foreground p-3 bg-muted/50 rounded-lg">
            <p className="font-bold mb-2 text-foreground">What is this?</p>
            <p>You can choose which AI model powers Mushi's brain. 'Anime Expert' is specialized for anime topics, while 'Qwen' is a general-purpose model. 'Gemini' is a powerful cloud-based model.</p>
          </div>
        </aside>

        {/* Main chat window area */}
        <main className="lg:col-span-3">
          {/* The ChatWindow component takes up the full space allocated to it */}
          <ChatWindow initialQuery={initialQuery} />
        </main>
      </div>
    </div>
  );
}

export default MushiAiView;
