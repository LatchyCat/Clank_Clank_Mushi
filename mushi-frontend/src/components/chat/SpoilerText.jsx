// mushi-frontend/src/components/chat/SpoilerText.jsx
import React, { useState } from 'react';

/**
 * Renders text that can be "spoiled" (hidden) or revealed.
 * The hidden text appears grayed out with "redacted" written over it.
 * Clicking the redacted text reveals the original content.
 *
 * @param {object} props
 * @param {string} props.children - The actual spoiler content to be displayed or hidden.
 * @param {boolean} props.globalShieldActive - If true, forces the spoiler text to be hidden and disables individual toggling.
 */
function SpoilerText({ children, globalShieldActive }) {
  // Local state to manage individual spoiler reveal, only active when global shield is off
  const [isRevealed, setIsRevealed] = useState(false);

  // Determine the effective revealed state:
  // If globalShieldActive is true, it forces the text to be hidden.
  // Otherwise, use the local 'isRevealed' state.
  const effectiveIsRevealed = globalShieldActive ? false : isRevealed;

  const toggleReveal = () => {
    // Only allow local toggling if the global spoiler shield is inactive
    if (!globalShieldActive) {
      setIsRevealed(prev => !prev);
    }
  };

  return (
    <span
      className={`relative inline-block cursor-pointer transition-all duration-200 ${
        effectiveIsRevealed ? 'text-gray-200' : 'text-transparent bg-gray-500 rounded px-1'
      }`}
      onClick={toggleReveal}
      title={effectiveIsRevealed ? "Click to hide spoiler" : "Click to reveal spoiler"}
    >
      {effectiveIsRevealed ? (
        children
      ) : (
        <span className="absolute inset-0 flex items-center justify-center text-gray-800 text-xs font-bold select-none pointer-events-none">
          redacted
        </span>
      )}
      <span className={effectiveIsRevealed ? '' : 'blur-sm'}>
        {children}
      </span>
    </span>
  );
}

export default SpoilerText;
