// mushi-frontend/src/components/chat/MushiFab.jsx
import React, { useState, useEffect } from 'react';

const snailImages = [
  '/mushi_snail_ace.png',
  '/mushi_snail_brook.png',
  '/mushi_snail_chopper.png',
  '/mushi_snail_cry.png',
  '/mushi_snail_flowers.png',
  '/mushi_snail_franky.png',
  '/mushi_snail_jump_happy.png',
  '/mushi_snail_luffy.png',
  '/mushi_snail_nami.png',
  '/mushi_snail_robin.png',
  '/mushi_snail_sabo.png',
  '/mushi_snail_sanji.png',
  '/mushi_snail_tri.png',
  '/mushi_snail_usopp.png',
  '/mushi_snail_weirdo.png',
  '/mushi_snail_zoro.png'
];

const MushiFab = ({ onClick }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentImageIndex(prevIndex => (prevIndex + 1) % snailImages.length);
    }, 20000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    // FIX: Changed z-50 to a higher value like z-[90]
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-full shadow-lg hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background focus:ring-pink-400 transition-all duration-200 z-[90] group"
      title="Ask Mushi"
      aria-label="Ask Mushi AI"
    >
      <img
        src={snailImages[currentImageIndex]}
        alt="Mushi Snail Icon"
        className="w-7 h-7 object-contain transition-transform group-hover:rotate-12"
      />
    </button>
  );
};

export default MushiFab;
