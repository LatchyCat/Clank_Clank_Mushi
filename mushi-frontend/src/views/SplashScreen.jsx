// mushi-frontend/src/views/SplashScreen.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons';

import { api } from '@/services/api';
import LLMInfoModal from '../components/common/LLMInfoModal';
import useSearch from '@/components/hooks/useSearch';
import Suggestion from '@/components/anime/searchbar/Suggestion';

const splashImages = [
  '/all_saints_marine.jpg', '/angry_pirates.jpg', '/awakened_lucio.jpg',
  '/axe_swing.jpg', '/bonny_cry.jpg', '/bonny_knockout.jpg',
  '/captured.png', '/crew_eating.jpg', '/dragon_crew.jpg',
  '/dragon_sipping_wine.jpg', '/fighting_kuzino.jpg', '/flying_kobe_friends.jpg',
  '/franky_robot.jpg', '/garp_mad.jpg', '/garp_power_punch.jpg',
  '/giant_fatty.jpg', '/ginny_mad.png', '/ginny_shocked.jpg',
  '/hair_flash.png', '/happy_ginny.jpg', '/heart_attack.png',
  '/jimbe_sanji_lab.jpg', '/kobe_crew_shocked.jpg', '/kobe_impact.jpg',
  '/kobe_pirate_island_hand.jpg', '/kuma_dad_dead.png', '/kuma_explosion.jpg',
  '/kuma_rage_bomb.jpg', '/kuma_smoke_mad.jpg', '/kuma_wanted_poster.jpg',
  '/kuma_women_dragon.jpg', '/kuza_clones_colors.jpg', '/luffy_eat.png',
  '/luffy_goggles.png', '/luffy_gross.png', '/luffy_gross2.png',
  '/luffy_idea.png', '/luffy_punch_kizano_stars.jpg', '/luffy_sorring.png',
  '/marine_ships.jpg', '/nami_ass.jpg', '/nika_god_grab_kuzo_lab.jpg',
  '/pirate_island_eyes.jpg', '/pirate_island_smash.jpg', '/pirate_island_smash_two.jpg',
  '/pirate_ship_explosion_colors.jpg', '/punk_nose.png', '/radar_sanji.jpg',
  '/real_mega_robot.jpg', '/saint_bonny_flying.jpg', '/saint_satan_portal.jpg',
  '/saint_saturn.jpg', '/saint_saturn_watching_kizano_punch.jpg', '/sanji_mushi_snail_lab.jpg',
  '/scared_crew.jpg', '/ship_vegapunk.jpg', '/skeloton_marine.jpg',
  '/star_night_ship.jpg', '/students_kobe.jpg', '/tbc_saint_eyes.jpg',
  '/teach_kobe.jpg', '/vega_all_minds.jpg', '/vega_beam_fingers.jpg',
  '/vega_beam_fingers_two.jpg', '/vega_cartoon_minds.jpg', '/vega_geeking.jpg',
  '/vega_kuma_bonny.jpg', '/zoro_fight_awaken_luci.jpg', '/zoro_fire_sword_stance.jpg',
  '/zoro_fire_swords.jpg', '/zoro_gross.png', '/zoro_sleeping.jpg'
];

const NAV_LINKS = [
  { to: "/home", label: "Home" },
  { to: "/mushi_ai", label: "Mushi AI" },
  { to: "/search", label: "Anime Search" },
  { to: "/data_insights", label: "Data Insights" },
];

function SplashScreen() {
  const navigate = useNavigate();
  const {
    searchValue,
    setSearchValue,
    isFocused,
    setIsFocused,
    debouncedValue,
    suggestionRef,
    handleBlur,
  } = useSearch();

  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isMenuModalOpen, setIsMenuModalOpen] = useState(false);
  // Use a static fallback for top search terms as this is not a critical feature
  const topSearch = [
    { id: 'search-one-piece', title: "One Piece", link: "/search?keyword=One%20Piece" },
    { id: 'search-jujutsu-kaisen', title: "Jujutsu Kaisen", link: "/search?keyword=Jujutsu%20Kaisen" },
    { id: 'search-frieren', title: "Frieren: Beyond Journey's End", link: "/search?keyword=Frieren%3A%20Beyond%20Journey's%20End" },
  ];
  const [adminPassword, setAdminPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [isLLMModalOpen, setIsLLMModalOpen] = useState(false);

  useEffect(() => {
    const imageInterval = setInterval(() => {
      setCurrentImageIndex(prevIndex => (prevIndex + 1) % splashImages.length);
    }, 7000);
    return () => clearInterval(imageInterval);
  }, []);

  const handleSearchSubmit = useCallback(() => {
    if (!searchValue.trim()) return;
    navigate(`/search?keyword=${encodeURIComponent(searchValue.trim())}`);
  }, [searchValue, navigate]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === "Enter") handleSearchSubmit();
  }, [handleSearchSubmit]);

  const handleAdminLogin = (e) => {
    e.preventDefault();
    setPasswordError('');
    const CORRECT_ADMIN_PASSWORD = 'mushisecurepassword';
    if (adminPassword === CORRECT_ADMIN_PASSWORD) {
      navigate('/admin_data');
    } else {
      setPasswordError("Eeeh~ That's not Mushi's secret password, Gomen'nasai! (T_T)");
    }
  };

  return (
    <div className="relative min-h-screen w-full bg-neutral-950 text-white overflow-x-hidden">
      <div className="absolute top-0 z-[-1] h-screen w-screen bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]"></div>

      <div className="w-full max-w-[1300px] mx-auto pt-12 relative max-[1350px]:w-full max-[1350px]:px-8 max-[780px]:px-4 max-[520px]:px-0 max-[520px]:pt-6">
        <nav className="relative w-full z-50">
          <div className="w-fit flex gap-x-12 mx-auto font-semibold max-[780px]:hidden">
            {NAV_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className="hover:text-pink-400 transition-colors">
                {link.label}
              </Link>
            ))}
          </div>
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

        <div className="min-h-[480px] bg-black/20 backdrop-blur-sm border border-white/10 rounded-[40px] flex relative mt-7 max-[780px]:w-full items-stretch max-[780px]:rounded-[30px] max-[520px]:rounded-none max-[520px]:min-h-fit max-[520px]:pb-4 max-[520px]:mt-4">
          <div className="h-auto flex flex-col w-[700px] relative z-40 px-20 py-10 max-[1200px]:py-12 max-[780px]:px-12 max-[780px]:w-full max-[520px]:py-4 max-[520px]:px-8">
            <h1 className="text-4xl font-extrabold tracking-wide max-[520px]:text-3xl max-[520px]:text-center bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400 drop-shadow-lg">
              Clank Clank Mushi <span className="text-2xl whitespace-nowrap">(ﾉ´ヮ´)ﾉ*</span>
            </h1>

            <div className="relative w-full">
              <div className="w-full flex gap-x-3 mt-6">
                <input
                  type="text"
                  placeholder="Search anime..."
                  className="w-full py-3 px-6 rounded-xl bg-white text-lg text-black placeholder:text-gray-500"
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={handleBlur}
                  onKeyDown={handleKeyDown}
                />
                <button className="bg-pink-400 text-black py-3 px-4 rounded-xl font-extrabold" onClick={handleSearchSubmit}><FontAwesomeIcon icon={faMagnifyingGlass} className="text-lg" /></button>
              </div>
              {isFocused && debouncedValue && (
                <div ref={suggestionRef} className="absolute w-full z-50">
                  <Suggestion keyword={debouncedValue} />
                </div>
              )}
            </div>

            <div className="mt-4 text-sm leading-relaxed max-[520px]:text-xs">
              <span className="font-semibold text-gray-300">Top Search: </span>
              {topSearch.map((item, index) => (
                <React.Fragment key={item.id || index}>
                  <Link to={item.link} className="text-gray-400 hover:text-pink-300 hover:underline">
                    {item.title}
                  </Link>
                  {index < topSearch.length - 1 && ', '}
                </React.Fragment>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row gap-4 mt-8">
              <Link to="/home" className="flex-1">
                <button className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-6 rounded-xl font-bold text-lg transform hover:scale-105 transition-transform">Explore Mushi's World</button>
              </Link>
              <Link to="/mushi_ai" className="flex-1">
                 <button className="w-full bg-gradient-to-r from-indigo-500 to-blue-500 text-white py-3 px-6 rounded-xl font-bold text-lg transform hover:scale-105 transition-transform">Chat with Mushi AI!</button>
              </Link>
            </div>

            <div className="mt-10 p-6 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 max-w-lg w-full">
              <h3 className="text-xl font-bold mb-4 text-purple-300 text-center">Admin Area 🤫</h3>
              <form onSubmit={handleAdminLogin} className="flex flex-col gap-4">
                <input type="password" value={adminPassword} onChange={(e) => setAdminPassword(e.target.value)} placeholder="Enter Mushi's secret password~" className="w-full p-3 rounded-lg bg-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 border border-white/20" />
                {passwordError && <p className="text-red-300 text-sm text-center font-medium">{passwordError}</p>}
                <button type="submit" className="w-full py-2 bg-gradient-to-r from-red-400 to-pink-400 text-white font-bold rounded-lg transform hover:scale-105 transition-transform">Access Admin Area</button>
              </form>
            </div>
          </div>

          <div className="h-full w-[600px] absolute right-0 max-[780px]:hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-neutral-950/80 via-neutral-950/20 to-transparent z-10"></div>
            {splashImages.map((imageSrc, index) => (
              <img
                key={imageSrc}
                src={imageSrc}
                alt={`Splash background ${index + 1}`}
                className={`absolute inset-0 w-full h-full object-cover rounded-r-[40px] transition-opacity duration-1000 ease-in-out ${
                  index === currentImageIndex ? 'opacity-100' : 'opacity-0'
                }`}
              />
            ))}
          </div>
        </div>

        <footer className="mt-10 text-center pb-4 text-sm text-gray-400">
          <p>© Clank Clank Mushi. All rights reserved.</p>
          <button onClick={() => setIsLLMModalOpen(true)} className="mt-2 text-purple-300 underline hover:text-purple-200 transition-colors">What is an LLM?~</button>
        </footer>

        <LLMInfoModal isOpen={isLLMModalOpen} onClose={() => setIsLLMModalOpen(false)} />
      </div>
    </div>
  );
}

export default SplashScreen;
