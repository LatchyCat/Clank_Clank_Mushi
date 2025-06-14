import React from 'react';

function LLMInfoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black bg-opacity-80"
      onClick={onClose}
    >
      <div
        className="bg-gray-800 text-white p-6 rounded-lg shadow-xl relative max-w-md w-[90%]"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-white text-2xl"
          aria-label="Close modal"
        >
          &times;
        </button>
        <h2 className="text-xl font-bold mb-4 text-indigo-400">What is an LLM?</h2>
        <p className="text-base leading-relaxed">
          A Large Language Model (LLM) is an AI system trained to understand and generate human language. It powers the intelligent chat and insight features of Clank Clank Mushi.
        </p>
      </div>
    </div>
  );
}

export default LLMInfoModal;
