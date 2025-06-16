import React from 'react';
import { PiSnail } from "react-icons/pi";

const MushiFab = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-full shadow-lg hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background focus:ring-pink-400 transition-all duration-200 z-50 group"
      title="Ask Mushi"
      aria-label="Ask Mushi AI"
    >
      <PiSnail size={28} className="transition-transform group-hover:rotate-12" />
    </button>
  );
};

export default MushiFab;
