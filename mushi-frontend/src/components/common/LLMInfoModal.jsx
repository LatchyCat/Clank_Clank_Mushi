// mushi-frontend/src/components/common/LLMInfoModal.jsx
import React from 'react';
import { X } from 'lucide-react';

/**
 * A modal that explains what an LLM is in the context of the Mushi app.
 *
 * @param {object} props
 * @param {boolean} props.isOpen - Controls if the modal is visible.
 * @param {() => void} props.onClose - Function to call to close the modal.
 */
function LLMInfoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    // Overlay to dim the background
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-[200]"
      onClick={onClose}
    >
      {/* Modal Content */}
      <div
        className="relative bg-neutral-900 border border-purple-500/50 rounded-2xl p-8 max-w-2xl w-full m-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white hover:bg-white/10 rounded-full p-2"
          aria-label="Close modal"
        >
          <X size={24} />
        </button>

        <h2 className="text-3xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400">
          What is an LLM?
        </h2>

        <div className="text-gray-300 space-y-4">
          <p>
            An LLM, or **Large Language Model**, is the technology that powers Mushi's brain! Think of it as a very advanced AI that has been trained on a massive amount of text and data from all over the internet.
          </p>
          <p>
            This training allows it to understand and generate human-like text, answer questions, summarize information, and even have creative conversations.
          </p>
          <p>
            In our app, Mushi uses a special "fine-tuned" LLM, which means it has extra training focused specifically on anime and manga. This helps it give you more accurate and relevant answers about your favorite shows!
          </p>
          <p className="mt-6 text-sm text-purple-300">
            When you see the option to choose a provider (like Gemini or Ollama), you're choosing which powerful AI engine Mushi should use to think. It's like picking which library Mushi should visit to find an answer for you!
          </p>
        </div>
      </div>
    </div>
  );
}

export default LLMInfoModal;
