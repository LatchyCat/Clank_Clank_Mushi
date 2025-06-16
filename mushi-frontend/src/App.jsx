// mushi-frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet, Navigate } from 'react-router-dom';

// Import Layout Components
import TopNav from './components/navigation/TopNav';
import FooterNav from './components/navigation/FooterNav';
import MushiFab from './components/chat/MushiFab';
import ChatModal from './components/chat/ChatModal';

// Import Views (SplashScreen is new, LandingView is replaced)
import SplashScreen from './views/SplashScreen'; // NEW: Replaces LandingView for the root route
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

// AppLayout remains the same, acting as the shared UI for the main application.
// It receives props for the carousel and renders the active route via <Outlet />.
const AppLayout = ({ images, currentIndex }) => {
  const [isChatOpen, setIsChatOpen] = useState(false); // State for the chat modal

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground font-inter">
      <TopNav images={images} currentIndex={currentIndex} />
      <main className="flex-grow p-6">
        <Outlet />
      </main>
      <FooterNav images={images} currentIndex={currentIndex} />

      {/* Mushi AI Chat Components */}
      <MushiFab onClick={() => setIsChatOpen(true)} />
      <ChatModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  );
};

function App() {
  // State for the background carousel remains in App, so it's shared by TopNav and FooterNav.
  const images = [
    '/luffy_idea.png',
    '/luffy_gross.png',
    '/zoro_gross.png',
    '/ginny_mad.png',
    '/captured.png',
    '/hair_flash.png',
    '/heart_attack.png',
    '/kuma_dad_dead.png',
    '/luffy_eat.png',
    '/luffy_goggles.png',
    '/luffy_gross2.png',
    '/luffy_sorring.png',
    '/punk_nose.png'
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 12000); // Rotate every 12 seconds
    return () => clearInterval(interval);
  }, [images.length]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<SplashScreen />} />

        <Route element={<AppLayout images={images} currentIndex={currentIndex} />}>
          <Route path="/home" element={<HomeView />} />
          <Route path="/mushi_ai" element={<MushiAiView />} />

          {/* Update the search route path for clarity */}
          <Route path="/search" element={<AnimeSearchView />} />

          {/* Add the new A-Z List route */}
          <Route path="/az-list" element={<AtoZListView />} />
          <Route path="/az-list/:letter" element={<AtoZListView />} />

          <Route path="/anime/details/:animeId" element={<AnimeDetailView />} />
          <Route path="/watch/:animeId/:episodeId" element={<WatchView />} />
          <Route path="/anime_category" element={<AnimeCategoryView />} />
          <Route path="/anime/character/:characterId" element={<CharacterDetailView />} />
          <Route path="/anime/actors/:actorId" element={<VoiceActorDetailView />} />
          <Route path="/data_insights" element={<DataView />} />
          <Route path="/admin_data" element={<AdminView />} />

          {/* Old search path redirect (optional but good) */}
          <Route path="/anime_search" element={<Navigate to="/search" replace />} />
        </Route>

        <Route path="/app" element={<Navigate to="/home" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
