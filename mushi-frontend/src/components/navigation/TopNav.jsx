// mushi-frontend/src/components/navigation/TopNav.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars } from '@fortawesome/free-solid-svg-icons';

// CORRECTED IMPORTS: Using the '@' alias from your vite.config.js
import Sidebar from '@/src/components/navigation/Sidebar';
import WebSearch from '@/src/components/anime/searchbar/WebSearch';
import MobileSearch from '@/src/components/anime/searchbar/MobileSearch';


function TopNav({ images, currentIndex }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleHamburgerClick = () => setIsSidebarOpen(true);
  const handleCloseSidebar = () => setIsSidebarOpen(false);

  return (
    <>
      <Sidebar isOpen={isSidebarOpen} onClose={handleCloseSidebar} />
      <nav className="relative p-4 h-28 flex items-center z-40 overflow-hidden">
        {/* KEPT (from Mushi): The signature background image carousel */}
        <img
          src={images[currentIndex]}
          alt={`Background image ${currentIndex + 1}`}
          className="absolute inset-0 w-full h-full object-cover transition-opacity duration-1000"
          style={{ opacity: 0.2 }}
        />
        {/* MERGED: Mushi's overlay, now with a dynamic opacity from Zenime's scroll effect */}
        <div
          className={`absolute inset-0 bg-purple-900 transition-opacity duration-300 z-0 ${
            isScrolled ? 'opacity-60' : 'opacity-35'
          }`}
        ></div>

        <div className="container mx-auto flex justify-between items-center relative z-10 text-white w-full">
          {/* Left Side: Hamburger Menu and Brand */}
          <div className="flex items-center gap-x-6">
            <FontAwesomeIcon icon={faBars} className="text-2xl text-white cursor-pointer" onClick={handleHamburgerClick} />
            <Link to="/home" className="text-white text-3xl font-extrabold hover:text-pink-300 transition-colors duration-300" title="Home">
              Clank Clank Mushi
            </Link>
          </div>

          {/* Center: Desktop Search Bar (from Zenime) */}
          <div className="hidden lg:flex flex-grow justify-center px-8">
             <WebSearch />
          </div>

          {/* Right Side: Mushi's Core Navigation Links (STYLES NOW INLINED) */}
          <div className="hidden lg:flex items-center space-x-2">
            <Link to="/home" className="text-white bg-white/10 border border-white/20 rounded-full px-4 py-2 hover:text-pink-200 hover:bg-white/20 hover:shadow-lg hover:border-pink-300 transition-all duration-300 text-base font-medium inline-block whitespace-nowrap">Home</Link>
            <Link to="/mushi_ai" className="text-white bg-white/10 border border-white/20 rounded-full px-4 py-2 hover:text-pink-200 hover:bg-white/20 hover:shadow-lg hover:border-pink-300 transition-all duration-300 text-base font-medium inline-block whitespace-nowrap">Mushi AI</Link>
            <Link to="/search" className="text-white bg-white/10 border border-white/20 rounded-full px-4 py-2 hover:text-pink-200 hover:bg-white/20 hover:shadow-lg hover:border-pink-300 transition-all duration-300 text-base font-medium inline-block whitespace-nowrap">Anime Search</Link>
            <Link to="/data_insights" className="text-white bg-white/10 border border-white/20 rounded-full px-4 py-2 hover:text-pink-200 hover:bg-white/20 hover:shadow-lg hover:border-pink-300 transition-all duration-300 text-base font-medium inline-block whitespace-nowrap">Data Insights</Link>
            <Link to="/admin_data" className="text-yellow-300 bg-yellow-500/10 border border-yellow-400/20 rounded-full px-4 py-2 hover:text-yellow-200 hover:bg-yellow-500/20 hover:shadow-lg hover:border-yellow-300 transition-all duration-300 text-base font-medium inline-block whitespace-nowrap">Admin Panel</Link>
          </div>
        </div>

        {/* Mobile search bar. Needs careful placement to avoid overlapping content */}
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-full px-4 lg:hidden">
            <MobileSearch />
        </div>
      </nav>
    </>
  );
}

export default TopNav;
