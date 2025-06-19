// mushi-frontend/src/components/common/ReceiverIcon.jsx
import React from 'react';

const ReceiverIcon = ({ direction = 'right', size = 24, className = '' }) => {
  const rotation = direction === 'left' ? 'scale(-1, 1)' : '';

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      transform={rotation}
      style={{ overflow: 'visible' }} // Prevents clipping of the icon
    >
      <path d="M8 3.48a4.5 4.5 0 0 1 7.1 2.34c1.15 2.2 1.34 4.78.58 7.26a10.99 10.99 0 0 1-2.22 3.65c-2.45 2.87-4.46 4.28-4.46 4.28" />
      <path d="M16 19s-2-1.41-4.46-4.28a10.99 10.99 0 0 1-2.22-3.65c-.76-2.48-.57-5.06.58-7.26a4.5 4.5 0 0 1 7.1-2.34" />
      <path d="M16.5 21a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z" />
      <path d="M7.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z" />
    </svg>
  );
};

export default ReceiverIcon;
