// mushi-frontend/src/components/chat/SpoilerText.jsx
import React, { useState } from 'react';

function SpoilerText({ children }) {
  const [isRevealed, setIsRevealed] = useState(false);

  // A single click handler now controls the entire block of text.
  const toggleReveal = () => {
    setIsRevealed(prev => !prev);
  };

  return (
    <span
      onClick={toggleReveal}
      title={isRevealed ? "Click to hide spoiler" : "Click to reveal spoiler"}
      // The cursor and background are applied to the entire block as one unit.
      className={`cursor-pointer transition-colors duration-200 rounded px-1 ${
        isRevealed ? 'text-gray-200 bg-transparent' : 'text-transparent bg-purple-500/50'
      }`}
    >
      {/* The text itself is passed as children and is revealed or blurred together. */}
      {children}
    </span>
  );
}

export default SpoilerText;
