// mushi-frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';

// Import Layout Components
import TopNav from './components/navigation/TopNav';
import FooterNav from './components/navigation/FooterNav';

// Import Views
import LandingView from './views/LandingView';
import HomeView from './views/HomeView';
import MushiAiView from './views/MushiAiView';
import AnimeSearchView from './views/AnimeSearchView';
import AnimeDetailView from './views/AnimeDetailView';
import AnimeCategoryView from './views/AnimeCategoryView';
import CharacterDetailView from './views/CharacterDetailView';
import VoiceActorDetailView from './views/VoiceActorDetailView';
import DataView from './views/DataView';
import AdminView from './views/AdminView'; // NEW: Import AdminView

// AppLayout now accepts images and currentIndex as props, and passes them down
const AppLayout = ({ images, currentIndex }) => (
  <div className="min-h-screen flex flex-col bg-gray-900 text-gray-100 font-inter">
    <TopNav images={images} currentIndex={currentIndex} /> {/* Pass props to TopNav */}
    <main className="flex-grow p-6">
      <Outlet /> {/* Renders the active nested route */}
    </main>
    <FooterNav images={images} currentIndex={currentIndex} /> {/* Pass props to FooterNav */}
  </div>
);

function App() {
  // Array of image paths for the carousel, now managed in the main App function
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

  // Auto-rotate the carousel every 12 seconds, managing state here for both navs
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 12000); // Rotate every 12 seconds

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, [images.length]); // Re-run effect if image count changes

  return (
    <Router>
      <Routes>
        {/* Route for the marketing/info landing page, which now includes admin login */}
        <Route path="/" element={<LandingView />} />

        {/* Nested routes for the main application, all using AppLayout.
            Pass images and currentIndex to AppLayout. */}
        <Route path="/app" element={<AppLayout images={images} currentIndex={currentIndex} />}>
          <Route index element={<HomeView />} />
          <Route path="mushi_ai" element={<MushiAiView />} />
          <Route path="anime_search" element={<AnimeSearchView />} />
          <Route path="anime/details/:animeId" element={<AnimeDetailView />} />
          <Route path="anime_category" element={<AnimeCategoryView />} />
          <Route path="anime/character/:characterId" element={<CharacterDetailView />} />
          <Route path="anime/actors/:actorId" element={<VoiceActorDetailView />} />
          <Route path="data_insights" element={<DataView />} />
          <Route path="admin_data" element={<AdminView />} /> {/* Route for Admin View (Data Ingestion) */}

        </Route>
      </Routes>
    </Router>
  );
}

export default App;
