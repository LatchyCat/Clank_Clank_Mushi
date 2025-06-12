// mushi-frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';

// Import Layout Components
import TopNav from './components/navigation/TopNav';
import FooterNav from './components/navigation/FooterNav';

// Import Views
import LandingPage from './views/LandingPage';
import HomeView from './views/HomeView';
import ChatView from './views/ChatView';
import DataView from './views/DataView';

// The AppLayout component is now cleaner, acting as a structural wrapper.
const AppLayout = () => (
  <div className="min-h-screen flex flex-col bg-gray-900 text-gray-100 font-inter">
    <TopNav />
    <main className="flex-grow p-6">
      <Outlet /> {/* Renders the active nested route */}
    </main>
    <FooterNav />
  </div>
);

function App() {
  return (
    <Router>
      <Routes>
        {/* Route for the marketing/info landing page */}
        <Route path="/" element={<LandingPage />} />

        {/* Nested routes for the main application, all using AppLayout */}
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<HomeView />} />
          <Route path="chat" element={<ChatView />} />
          <Route path="data" element={<DataView />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
