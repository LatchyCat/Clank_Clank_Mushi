import React from 'react';
import { Sparkles } from 'lucide-react';

/**
 * Renders a row of follow-up question buttons below the chat.
 * When clicked, each button will call `onQuestionClick` with the question text.
 *
 * @param {object} props
 * @param {string[]} props.questions - Array of follow-up question strings.
 * @param {(question: string) => void} props.onQuestionClick - Callback when a suggestion is clicked.
 */
function QuestionPrompts({ questions, onQuestionClick }) {
  if (!Array.isArray(questions) || questions.length === 0) return null;

  return (
    <div className="px-4 py-3 border border-purple-500/20 rounded-xl mb-4 bg-white/5 shadow-lg">
      <p className="text-sm text-gray-300 mb-3 font-medium">Mushi suggests asking...</p>
      <div className="flex flex-wrap gap-3">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="flex items-center gap-2 bg-gradient-to-r from-purple-600/50 to-pink-500/50 hover:from-purple-600 hover:to-pink-500 text-white text-sm font-medium py-2 px-4 rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-pink-400 shadow-md transform hover:scale-105"
          >
            <Sparkles size={16} className="text-pink-300"/>
            <span>{question}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default QuestionPrompts;
