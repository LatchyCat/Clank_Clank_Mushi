// mushi-frontend/src/components/navigation/FooterNav.jsx
import React from 'react';

// Accept images and currentIndex as props from the parent (AppLayout, which gets them from App.jsx)
function FooterNav({ images, currentIndex }) {
  return (
    <footer
      className="relative bg-gray-800 h-16 flex items-center justify-center // Compact height
                 border-t-4 border-indigo-500 text-gray-400 text-sm overflow-hidden" // Added relative and overflow-hidden for image
    >
      {/* Background Image Carousel - using the same image as TopNav, but with lower opacity */}
      <img
        src={images[currentIndex]}
        alt={`Footer background image ${currentIndex + 1}`}
        className="absolute inset-0 w-full h-full object-cover // object-cover to make image fit
                   transition-opacity duration-1000" // Smooth fade transition
        style={{ opacity: 0.2 }} // Make it more subtle for a footer background
      />

      {/* Overlay to ensure text readability */}
      <div className="absolute inset-0 bg-gray-900 opacity-65 z-0"></div>

      {/* Content Layer: Text - ensure it's above the image and overlay */}
      <p className="font-medium relative z-10"> Powered by the Clank Clank Mushi LLM | 2025 © </p>
    </footer>
  );
}

export default FooterNav;
