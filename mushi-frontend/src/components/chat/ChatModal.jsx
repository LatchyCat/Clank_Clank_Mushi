// mushi-frontend/src/components/chat/ChatModal.jsx
import React, { useEffect } from 'react';
import ChatWindow from './ChatWindow';
import { X } from 'lucide-react';

const ChatModal = ({ isOpen, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  return (
    // Overlay
    <div
      className={`fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-300 ease-in-out z-[100] ${
        isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}
      onClick={onClose}
    >
      {/* Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-full max-w-4xl bg-neutral-900 shadow-2xl transform transition-transform duration-500 ease-in-out flex flex-col z-[101] border-l border-white/10 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        style={{
            backgroundImage: 'radial-gradient(circle at top right, rgba(120, 119, 198, 0.15), transparent 40%)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-4 border-b border-white/10 flex-shrink-0">
          <div className="flex items-center gap-3">
              <img src="/mushi_snail_luffy.png" alt="Mushi Snail" className="w-8 h-8"/>
              <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">Ask Mushi</h2>
          </div>
            <button
                onClick={onClose}
                className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-white/10 transition-colors"
                aria-label="Close chat"
            >
                <X size={24} />
            </button>
        </div>
        <div className="flex-grow overflow-hidden p-4">
            <ChatWindow />
        </div>
      </div>
    </div>
  );
};

export default ChatModal;
