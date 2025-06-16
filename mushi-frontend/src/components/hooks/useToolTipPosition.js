import { useRef } from 'react';

// A placeholder for the tooltip positioning logic.
// This will provide default values to prevent crashes.
function useToolTipPosition(hoveredItem, data) {
  const cardRefs = useRef([]);

  // Default positions
  const tooltipPosition = 'bottom-full mb-2'; // Position above the card
  const tooltipHorizontalPosition = 'left-1/2 -translate-x-1/2'; // Center horizontally

  return { tooltipPosition, tooltipHorizontalPosition, cardRefs };
}

export default useToolTipPosition;
