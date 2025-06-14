// mushi-frontend/src/components/navigation/TopNav.jsx
import React from 'react';
import { Link } from 'react-router-dom';

// Accept images and currentIndex as props from the parent (AppLayout, which gets them from App.jsx)
function TopNav({ images, currentIndex }) {
  return (
    <nav
      className="relative p-4 shadow-md h-28 // Fixed height for the nav banner
                 border-b-4 border-indigo-500 overflow-hidden" // Border and overflow hidden for carousel
    >
      {/* Background Image Carousel - uses props */}
      <img
        src={images[currentIndex]}
        alt={`Background image ${currentIndex + 1}`}
        className="absolute inset-0 w-full h-full object-cover // object-cover to make image fit the whole bar
                   transition-opacity duration-1000" // Smooth fade transition
        style={{ opacity: 1 }} // Ensure image is visible
      />

      {/* Overlay added with 35% opacity for tint */}
      <div className="absolute inset-0 bg-gray-900 opacity-35 z-0"></div>

      {/* Content Layer: Brand and Navigation Links */}
      <div className="container mx-auto flex justify-between items-center relative z-10 text-white">
        {/* Brand/Logo */}
        <Link
          to="/app"
          className="text-white text-3xl font-extrabold
                     hover:text-blue-400 transition-colors duration-300"
          title="Home"
        >
          Clank Clank Mushi
        </Link>

        {/* Navigation Links with enhanced styling */}
        <div className="space-x-4">
          <Link
            to="/app"
            className="text-white bg-gray-800 border border-gray-600 rounded-md px-3 py-2
                       hover:text-indigo-200 hover:bg-gray-700 hover:shadow-lg hover:border-indigo-500
                       transition-all duration-300 text-lg font-medium inline-block"
          >
            Home
          </Link>
          <Link
            to="/app/mushi_ai"
            className="text-white bg-gray-800 border border-gray-600 rounded-md px-3 py-2
                       hover:text-indigo-200 hover:bg-gray-700 hover:shadow-lg hover:border-indigo-500
                       transition-all duration-300 text-lg font-medium inline-block"
          >
            Mushi AI
          </Link>
          {/* Link to Anime Search View */}
          <Link
            to="/app/anime_search"
            className="text-white bg-gray-800 border border-gray-600 rounded-md px-3 py-2
                       hover:text-indigo-200 hover:bg-gray-700 hover:shadow-lg hover:border-indigo-500
                       transition-all duration-300 text-lg font-medium inline-block"
          >
            Anime Search~
          </Link>
          {/* Link to Anime Category View */}
          <Link
            to="/app/anime_category"
            className="text-white bg-gray-800 border border-gray-600 rounded-md px-3 py-2
                       hover:text-indigo-200 hover:bg-gray-700 hover:shadow-lg hover:border-indigo-500
                       transition-all duration-300 text-lg font-medium inline-block"
          >
            Anime Categories~
          </Link>
          {/* Link to Data Insights View */}
          <Link
            to="/app/data_insights"
            className="text-white bg-gray-800 border border-gray-600 rounded-md px-3 py-2
                       hover:text-indigo-200 hover:bg-gray-700 hover:shadow-lg hover:border-indigo-500
                       transition-all duration-300 text-lg font-medium inline-block"
          >
            Data Insights~
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default TopNav;
