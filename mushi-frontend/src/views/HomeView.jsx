// mushi-frontend/src/views/HomeView.jsx
import React from 'react';

function HomeView() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <h1 className="text-5xl font-extrabold text-blue-400 mb-6 animate-pulse">
        Welcome to Clank Clank Mushi!
      </h1>
      <p className="text-xl text-gray-300 mb-8 max-w-2xl">
        Your ultimate companion for all things anime, manga, and One Piece lore.
        Chat with Mushi or explore our data!
      </p>
      <div className="flex space-x-4">
        <a href="/chat" className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors duration-300">
          Start Chatting
        </a>
        <a href="/data" className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 transition-colors duration-300">
          Explore Data
        </a>
      </div>
    </div>
  );
}

export default HomeView;
