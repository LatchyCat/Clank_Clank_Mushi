// mushi-frontend/src/components/navigation/TopNav.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars } from '@fortawesome/free-solid-svg-icons';
import { FaDiscord, FaGithub, FaTwitter, FaBell } from 'react-icons/fa';

import Sidebar from '@/components/navigation/Sidebar';
import WebSearch from '@/components/anime/searchbar/WebSearch';
import MobileSearch from '@/components/anime/searchbar/MobileSearch';
import TopNavMegaMenu from './TopNavMegaMenu';

const AnimatedSnail = () => (
    <div className="absolute -left-5 -bottom-2 group-hover:-left-4 transition-all duration-300">
        <img
            src="/mushi_snail_luffy.png"
            alt="Mushi Snail"
            className="w-8 h-8 transition-transform duration-500 ease-out transform group-hover:-rotate-12"
        />
    </div>
);

function TopNav({ images, currentIndex }) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);

    const handleHamburgerClick = () => setIsSidebarOpen(true);
    const handleCloseSidebar = () => setIsSidebarOpen(false);

    return (
        <>
            <Sidebar isOpen={isSidebarOpen} onClose={handleCloseSidebar} />
            <nav className="relative p-4 h-28 flex items-center z-[60] transition-all duration-300 ease-in-out">
                <div className="absolute inset-0 w-full h-full overflow-hidden z-[-1]">
                    <div
                        style={{ backgroundImage: `url(${images[currentIndex]})` }}
                        className="absolute inset-[-20px] w-[calc(100%+40px)] h-[calc(100%+40px)] bg-cover bg-center transition-all duration-1000"
                    ></div>
                    <div className="absolute inset-0 bg-purple-900/65 opacity-80"></div>
                </div>

                <div className="container mx-auto flex justify-between items-center relative z-10 text-white w-full">
                    {/* Left Side: Logo & Main Nav */}
                    <div className="flex items-center gap-x-6">
                        <FontAwesomeIcon icon={faBars} className="text-2xl text-white cursor-pointer" onClick={handleHamburgerClick} />
                        <Link to="/home" className="text-white text-3xl font-extrabold hover:text-pink-300 transition-colors duration-300 group relative pr-4" title="Home">
                            <AnimatedSnail />
                            Clank Clank Mushi
                        </Link>
                        {/* Desktop Main Links */}
                        <div className="hidden lg:flex items-center space-x-2">
                             <Link to="/home" className="px-4 py-2 rounded-md hover:text-pink-200 hover:bg-white/10 transition-colors text-base font-medium">Home</Link>

                            {/* --- FIX: Wrap link and menu in a single div to create a unified hover area --- */}
                            <div className="relative" onMouseEnter={() => setIsMegaMenuOpen(true)} onMouseLeave={() => setIsMegaMenuOpen(false)}>
                                <Link to="/search" className="px-4 py-2 rounded-md hover:text-pink-200 hover:bg-white/10 transition-colors text-base font-medium block">
                                    Anime Search
                                </Link>
                                <div className={`absolute top-full left-1/2 -translate-x-1/2 pt-4 transition-opacity duration-300 ${isMegaMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
                                    <div className="bg-neutral-900/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
                                        <TopNavMegaMenu />
                                    </div>
                                </div>
                            </div>

                            <Link to="/mushi_ai" className="px-4 py-2 rounded-md hover:text-pink-200 hover:bg-white/10 transition-colors text-base font-medium">Mushi AI</Link>
                        </div>
                    </div>

                    {/* Center Search Bar */}
                    <div className="hidden lg:flex flex-grow justify-center px-8">
                        <WebSearch />
                    </div>

                    {/* Right Side: Socials and Admin */}
                    <div className="hidden lg:flex items-center gap-x-3">
                         <div className="flex items-center gap-x-3 text-gray-300">
                             <a href="#" className="hover:text-white transition-colors" title="Discord"><FaDiscord size={20} /></a>
                             <a href="#" className="hover:text-white transition-colors" title="GitHub"><FaGithub size={20} /></a>
                             <a href="#" className="hover:text-white transition-colors" title="Twitter/X"><FaTwitter size={20} /></a>
                         </div>
                        <div className="w-px h-6 bg-white/20 mx-2"></div>
                        <button className="relative p-2 rounded-full hover:bg-white/10 text-gray-300 hover:text-white" title="Notifications from Mushi">
                            <FaBell size={20} />
                            <span className="absolute top-1.5 right-1.5 flex h-2.5 w-2.5">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pink-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-pink-500"></span>
                            </span>
                        </button>
                        <Link to="/admin_data" className="text-yellow-300 bg-yellow-500/10 border border-yellow-400/20 rounded-full px-4 py-2 hover:text-yellow-200 hover:bg-yellow-500/20 hover:shadow-lg hover:border-yellow-300 transition-all duration-300 text-sm font-medium inline-block whitespace-nowrap">Admin</Link>
                    </div>
                </div>

                <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 w-full px-4 lg:hidden">
                    <MobileSearch />
                </div>
            </nav>
        </>
    );
}

export default TopNav;
