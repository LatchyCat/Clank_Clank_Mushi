// mushi-frontend/src/views/SplashScreen.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMagnifyingGlass, faCircleArrowRight } from '@fortawesome/free-solid-svg-icons';

// --- Mushi Features ---
import LLMInfoModal from '../components/common/LLMInfoModal';

// --- Zenime Features ---
// This assumes you have a utility function to fetch top searches.
// If not, you can mock it or remove this section for now.
// import getTopSearch from '@/src/utils/getTopSearch.utils';

// MOCK: Mocking the Zenime API call for now.
const getTopSearch = async () => [
  { title: "One Piece", link: "/anime/details/21" },
  { title: "Jujutsu Kaisen", link: "/anime/details/51137" },
  { title: "Frieren: Beyond Journey's End", link: "/anime/details/52991" },
];

// MERGED: Navigation links now point to Mushi's routes.
const NAV_LINKS = [
  { to: "/home", label: "Home" },
  { to: "/mushi_ai", label: "Mushi AI" },
  { to: "/anime_search", label: "Anime Search" },
  { to: "/data_insights", label: "Data Insights" },
];

function SplashScreen() {
  const navigate = useNavigate();

  // State from Zenime
  const [search, setSearch] = useState("");
  const [isMenuModalOpen, setIsMenuModalOpen] = useState(false);
  const [topSearch, setTopSearch] = useState([]);

  // State from Mushi
  const [adminPassword, setAdminPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [isLLMModalOpen, setIsLLMModalOpen] = useState(false);

  // --- Logic from Zenime ---
  useEffect(() => {
    const fetchTopSearch = async () => {
      const data = await getTopSearch();
      if (data) setTopSearch(data);
    };
    fetchTopSearch();
  }, []);

  const handleSearchSubmit = useCallback(() => {
    if (!search.trim()) return;
    // NOTE: This now navigates to your existing Anime Search view
    navigate(`/anime_search?keyword=${encodeURIComponent(search.trim())}`);
  }, [search, navigate]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === "Enter") handleSearchSubmit();
  }, [handleSearchSubmit]);

  // --- Logic from Mushi ---
  const handleAdminLogin = (e) => {
    e.preventDefault();
    setPasswordError('');
    const CORRECT_ADMIN_PASSWORD = 'mushisecurepassword'; // Keep your password
    if (adminPassword === CORRECT_ADMIN_PASSWORD) {
      navigate('/admin_data'); // Navigate to the correct admin route
    } else {
      setPasswordError("Eeeh~ That's not Mushi's secret password, Gomen'nasai! (T_T)");
    }
  };

  return (
    // KEPT (from Mushi): The glowing radial background now serves as the page's base layer.
    <div className="relative min-h-screen w-full bg-neutral-950 text-white overflow-x-hidden">
      <div className="absolute top-0 z-[-1] h-screen w-screen bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]"></div>

      {/* KEPT (from Zenime): The main centered container structure */}
      <div className="w-full max-w-[1300px] mx-auto pt-12 relative max-[1350px]:w-full max-[1350px]:px-8 max-[780px]:px-4 max-[520px]:px-0 max-[520px]:pt-6">

        {/* --- Top Navigation (from Zenime, adapted for Mushi) --- */}
        <nav className="relative w-full z-50">
          <div className="w-fit flex gap-x-12 mx-auto font-semibold max-[780px]:hidden">
            {NAV_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className="hover:text-pink-400 transition-colors">
                {link.label}
              </Link>
            ))}
          </div>
          {/* Mobile Menu */}
          <div className="max-[780px]:block hidden max-[520px]:px-4">
            <button onClick={() => setIsMenuModalOpen(true)} className="p-2 flex items-center gap-x-2 group">
              <svg className="w-6 h-6 group-hover:text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
              <span className="font-semibold group-hover:text-pink-400">Menu</span>
            </button>
          </div>
          {isMenuModalOpen && (
            <div className="max-[780px]:block w-full hidden absolute top-10">
              <div className="bg-neutral-900/90 backdrop-blur-md w-full p-6 rounded-2xl flex flex-col gap-y-6 items-center border border-white/10">
                <button onClick={() => setIsMenuModalOpen(false)} className="self-end text-black text-xl absolute top-0 right-0 bg-white px-3 py-1 rounded-tr-xl rounded-bl-xl font-bold">×</button>
                {NAV_LINKS.map((link) => (
                  <Link key={link.to} to={link.to} onClick={() => setIsMenuModalOpen(false)} className="hover:text-pink-400 text-white text-lg">{link.label}</Link>
                ))}
              </div>
            </div>
          )}
        </nav>

        {/* --- Main Content Box (Structure from Zenime) --- */}
        <div className="min-h-[480px] bg-black/20 backdrop-blur-sm border border-white/10 rounded-[40px] flex relative mt-7 max-[780px]:w-full items-stretch max-[780px]:rounded-[30px] max-[520px]:rounded-none max-[520px]:min-h-fit max-[520px]:pb-4 max-[520px]:mt-4">

          <div className="h-auto flex flex-col w-[700px] relative z-40 px-20 py-10 max-[1200px]:py-12 max-[780px]:px-12 max-[780px]:w-full max-[520px]:py-4 max-[520px]:px-8">

            {/* MERGED: Using Mushi's expressive title with Zenime's layout */}
            <h1 className="text-5xl font-extrabold tracking-wide max-[520px]:text-4xl max-[520px]:text-center bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400 drop-shadow-lg">
              Clank Clank Mushi <span className="text-2xl">(ﾉ´ヮ´)ﾉ*</span>
            </h1>

            {/* KEPT (from Zenime): Search Bar */}
            <div className="w-full flex gap-x-3 mt-6">
              <input type="text" placeholder="Search anime..." className="w-full py-3 px-6 rounded-xl bg-white text-lg text-black placeholder:text-gray-500" value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={handleKeyDown} />
              <button className="bg-pink-400 text-black py-3 px-4 rounded-xl font-extrabold" onClick={handleSearchSubmit}><FontAwesomeIcon icon={faMagnifyingGlass} className="text-lg" /></button>
            </div>

            {/* KEPT (from Zenime): Top Search */}
            <div className="mt-4 text-sm leading-relaxed max-[520px]:text-xs">
              <span className="font-semibold text-gray-300">Top search: </span>
              {topSearch.map((item, index) => (
                <Link to={item.link} key={index} className="text-gray-400 hover:text-pink-300 hover:underline">{item.title}{index < topSearch.length - 1 && ', '}</Link>
              ))}
            </div>

            {/* MERGED: Using Mushi's dual buttons, styled like Zenime's */}
            <div className="flex flex-col sm:flex-row gap-4 mt-8">
              <Link to="/home" className="flex-1">
                <button className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-6 rounded-xl font-bold text-lg transform hover:scale-105 transition-transform">Explore Mushi's World</button>
              </Link>
              <Link to="/mushi_ai" className="flex-1">
                 <button className="w-full bg-gradient-to-r from-indigo-500 to-blue-500 text-white py-3 px-6 rounded-xl font-bold text-lg transform hover:scale-105 transition-transform">Chat with Mushi AI!</button>
              </Link>
            </div>

            {/* KEPT (from Mushi): The Admin Login Panel, restyled to fit */}
            <div className="mt-10 p-6 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 max-w-lg w-full">
              <h3 className="text-xl font-bold mb-4 text-purple-300 text-center">Admin Area 🤫</h3>
              <form onSubmit={handleAdminLogin} className="flex flex-col gap-4">
                <input type="password" value={adminPassword} onChange={(e) => setAdminPassword(e.target.value)} placeholder="Enter Mushi's secret password~" className="w-full p-3 rounded-lg bg-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 border border-white/20" />
                {passwordError && <p className="text-red-300 text-sm text-center font-medium">{passwordError}</p>}
                <button type="submit" className="w-full py-2 bg-gradient-to-r from-red-400 to-pink-400 text-white font-bold rounded-lg transform hover:scale-105 transition-transform">Access Admin Area</button>
              </form>
            </div>

          </div>

          {/* KEPT (from Zenime): The decorative image on the right */}
          <div className="h-full w-[600px] absolute right-0 max-[780px]:hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-neutral-950/80 via-neutral-950/20 to-transparent z-10"></div>
            <img src="/splash.webp" alt="Splash" className="bg-cover rounded-r-[40px] w-full h-full object-cover" />
          </div>
        </div>

        {/* MERGED: Footer combining Zenime's copyright with Mushi's LLM info link */}
        <footer className="mt-10 text-center pb-4 text-sm text-gray-400">
          <p>© Clank Clank Mushi. All rights reserved.</p>
          <button onClick={() => setIsLLMModalOpen(true)} className="mt-2 text-purple-300 underline hover:text-purple-200 transition-colors">What is an LLM?~</button>
        </footer>

        {/* KEPT (from Mushi): The modal component itself */}
        <LLMInfoModal isOpen={isLLMModalOpen} onClose={() => setIsLLMModalOpen(false)} />
      </div>
    </div>
  );
}

export default SplashScreen;
