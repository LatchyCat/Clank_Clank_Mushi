import React, { useEffect } from 'react';
import ChatWindow from './ChatWindow';
import { X } from 'lucide-react';

const ChatModal = ({ isOpen, onClose }) => {

  // Effect to handle 'Escape' key press
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
      className={`fixed inset-0 bg-black transition-opacity duration-300 ease-in-out z-[100] ${
        isOpen ? 'bg-opacity-70' : 'bg-opacity-0 pointer-events-none'
      }`}
      onClick={onClose}
    >
      {/* Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-full max-w-2xl bg-neutral-950 shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        onClick={(e) => e.stopPropagation()} // Prevent closing modal when clicking inside
      >
        <div className="flex justify-between items-center p-4 border-b border-white/10 flex-shrink-0">
            <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">Ask Mushi</h2>
            <button
                onClick={onClose}
                className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-white/10"
                aria-label="Close chat"
            >
                <X size={24} />
            </button>
        </div>
        <div className="flex-grow overflow-hidden p-2">
            <ChatWindow />
        </div>
      </div>
    </div>
  );
};

export default ChatModal;
