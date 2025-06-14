import React from 'react';

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
    <div className="px-4 py-3 border border-indigo-500 rounded-lg mb-4 bg-gray-800">
      <p className="text-sm text-gray-300 mb-2">Suggested questions based on your last query:</p>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="bg-gray-700 hover:bg-indigo-600 text-white text-sm font-medium py-2 px-4 rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            {/* Added a span with text-indigo-300 for the actual question text */}
            Question Suggestion: <span className="text-indigo-300">{question}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default QuestionPrompts;
