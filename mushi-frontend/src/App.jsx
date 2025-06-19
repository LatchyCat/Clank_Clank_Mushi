// mushi-frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet, Navigate, useLocation } from 'react-router-dom'; // <-- Import useLocation

// Import Layout Components
import TopNav from './components/navigation/TopNav';
import FooterNav from './components/navigation/FooterNav';
import MushiFab from './components/chat/MushiFab';
import ChatModal from './components/chat/ChatModal';

// Import Views
import SplashScreen from './views/SplashScreen';
import HomeView from './views/HomeView';
import MushiAiView from './views/MushiAiView';
import AnimeSearchView from './views/AnimeSearchView';
import AnimeDetailView from './views/AnimeDetailView';
import AnimeCategoryView from './views/AnimeCategoryView';
import CharacterDetailView from './views/CharacterDetailView';
import VoiceActorDetailView from './views/VoiceActorDetailView';
import DataView from './views/DataView';
import AdminView from './views/AdminView';
import WatchView from './views/WatchView';
import AtoZListView from './views/AtoZListView';

const AppLayout = ({ images, currentIndex }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const location = useLocation(); // <-- Get the current location

  // --- LOGIC TO CHOOSE FOOTER VARIANT ---
  // List of paths that should have a compact footer
  const compactFooterPaths = ['/mushi_ai', '/data_insights', '/admin_data'];
  const footerVariant = compactFooterPaths.includes(location.pathname) ? 'compact' : 'full';
  // --- END OF LOGIC ---

  return (
    <div className="relative min-h-screen w-full bg-neutral-950 text-foreground overflow-x-hidden flex flex-col">
      <div className="absolute top-0 left-0 z-[-2] h-full w-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]"></div>
      <TopNav images={images} currentIndex={currentIndex} />
      <main className="flex-grow p-4 md:p-6 lg:mt-0 mt-12">
        <Outlet />
      </main>
      {/* --- FIX: Pass the chosen variant to the FooterNav --- */}
      <FooterNav images={images} currentIndex={currentIndex} variant={footerVariant} />

      <MushiFab onClick={() => setIsChatOpen(true)} />
      <ChatModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  );
};

function App() {
  const images = [
    '/all_saints_marine.jpg',
    '/angry_pirates.jpg',
    '/awakened_lucio.jpg',
    '/axe_swing.jpg',
    '/bonny_cry.jpg',
    '/bonny_knockout.jpg',
    '/captured.png',
    '/crew_eating.jpg',
    '/dragon_crew.jpg',
    '/dragon_sipping_wine.jpg',
    '/fighting_kuzino.jpg',
    '/flying_kobe_friends.jpg',
    '/franky_robot.jpg',
    '/garp_mad.jpg',
    '/garp_power_punch.jpg',
    '/giant_fatty.jpg',
    '/ginny_mad.png',
    '/ginny_shocked.jpg',
    '/hair_flash.png',
    '/happy_ginny.jpg',
    '/heart_attack.png',
    '/jimbe_sanji_lab.jpg',
    '/kobe_crew_shocked.jpg',
    '/kobe_impact.jpg',
    '/kobe_pirate_island_hand.jpg',
    '/kuma_dad_dead.png',
    '/kuma_explosion.jpg',
    '/kuma_rage_bomb.jpg',
    '/kuma_smoke_mad.jpg',
    '/kuma_wanted_poster.jpg',
    '/kuma_women_dragon.jpg',
    '/kuza_clones_colors.jpg',
    '/luffy_eat.png',
    '/luffy_goggles.png',
    '/luffy_gross.png',
    '/luffy_gross2.png',
    '/luffy_idea.png',
    '/luffy_punch_kizano_stars.jpg',
    '/luffy_sorring.png',
    '/marine_ships.jpg',
    '/nami_ass.jpg',
    '/nika_god_grab_kuzo_lab.jpg',
    '/pirate_island_eyes.jpg',
    '/pirate_island_smash.jpg',
    '/pirate_island_smash_two.jpg',
    '/pirate_ship_explosion_colors.jpg',
    '/punk_nose.png',
    '/radar_sanji.jpg',
    '/real_mega_robot.jpg',
    '/saint_bonny_flying.jpg',
    '/saint_satan_portal.jpg',
    '/saint_saturn.jpg',
    '/saint_saturn_watching_kizano_punch.jpg',
    '/sanji_mushi_snail_lab.jpg',
    '/scared_crew.jpg',
    '/ship_vegapunk.jpg',
    '/skeloton_marine.jpg',
    '/star_night_ship.jpg',
    '/students_kobe.jpg',
    '/tbc_saint_eyes.jpg',
    '/teach_kobe.jpg',
    '/vega_all_minds.jpg',
    '/vega_beam_fingers.jpg',
    '/vega_beam_fingers_two.jpg',
    '/vega_cartoon_minds.jpg',
    '/vega_geeking.jpg',
    '/vega_kuma_bonny.jpg',
    '/zoro_fight_awaken_luci.jpg',
    '/zoro_fire_sword_stance.jpg',
    '/zoro_fire_swords.jpg',
    '/zoro_gross.png',
    '/zoro_sleeping.jpg'
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 7000);
    return () => clearInterval(interval);
  }, [images.length]);

 return (
    <Router>
      <Routes>
        <Route path="/" element={<SplashScreen />} />

        <Route element={<AppLayout images={images} currentIndex={currentIndex} />}>
          <Route path="/home" element={<HomeView />} />
          <Route path="/mushi_ai" element={<MushiAiView />} />
          <Route path="/search" element={<AnimeSearchView />} />
          <Route path="/az-list" element={<AtoZListView />} />
          <Route path="/az-list/:letter" element={<AtoZListView />} />
          <Route path="/anime/details/:animeId" element={<AnimeDetailView />} />
          <Route path="/watch/:animeId/:episodeId?" element={<WatchView />} />
          <Route path="/anime_category" element={<AnimeCategoryView />} />
          <Route path="/anime/character/:characterId" element={<CharacterDetailView />} />
          <Route path="/anime/actors/:actorId" element={<VoiceActorDetailView />} />
          <Route path="/data_insights" element={<DataView />} />
          <Route path="/admin_data" element={<AdminView />} />
          <Route path="/anime_search" element={<Navigate to="/search" replace />} />
        </Route>

        <Route path="/app" element={<Navigate to="/home" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
