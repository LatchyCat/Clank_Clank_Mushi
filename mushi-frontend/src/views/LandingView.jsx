// mushi-frontend/src/views/LandingView.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // For programmatic navigation
import LLMInfoModal from '../components/common/LLMInfoModal'; // Re-import LLMInfoModal

/**
 * LandingView component serves as the initial marketing/info page.
 * It now includes options for users to enter as a general visitor, chat with Mushi AI,
 * or access an admin area via password.
 */
function LandingView() {
  const navigate = useNavigate();
  const [adminPassword, setAdminPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [isLLMModalOpen, setIsLLMModalOpen] = useState(false); // State for LLMInfoModal

  // NOTE: For a real application, this password would be securely managed and verified
  // on the backend. For this demo, it's a simple client-side check.
  const CORRECT_ADMIN_PASSWORD = 'mushisecurepassword'; // Senpai, please choose a strong password!

  const handleAdminLogin = (e) => {
    e.preventDefault();
    setPasswordError(''); // Clear previous errors

    if (adminPassword === CORRECT_ADMIN_PASSWORD) {
      console.log("Admin login successful, Senpai! Redirecting to admin data ingestion... ✨");
      navigate('/app/admin_data'); // Navigate to the new admin data ingestion route
    } else {
      setPasswordError("Eeeh~ That's not Mushi's secret password, Gomen'nasai! (T_T)");
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gray-900 text-gray-100 p-6 text-center">
      <h1 className="text-5xl font-extrabold text-indigo-400 mb-6 animate-pulse">
        Welcome to Clank Clank Mushi! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h1>
      <p className="text-xl leading-relaxed max-w-2xl mb-8">
        Your ultimate AI companion for all things anime, manga, and the Grand Line!
        Mushi is here to provide sparkling insights, news, and lore, desu!~
      </p>

      {/* Main Entry Points: Visitor/User */}
      <div className="flex flex-col sm:flex-row gap-4 mb-12">
        <button
          onClick={() => navigate('/app')}
          className="px-8 py-3 bg-indigo-600 text-white font-bold text-lg rounded-full shadow-lg
                     hover:bg-indigo-700 transform hover:scale-105 transition-all duration-300"
        >
          Explore Mushi's World ~
        </button>
        <button
          onClick={() => navigate('/app/mushi_ai')}
          className="px-8 py-3 bg-gray-700 text-white font-bold text-lg rounded-full shadow-lg
                     hover:bg-gray-600 transform hover:scale-105 transition-all duration-300"
        >
          Chat with Mushi AI! ~
        </button>
      </div>

      {/* Admin Login Section */}
      <div className="mt-12 p-6 bg-gray-800 rounded-lg shadow-xl border border-gray-700 max-w-md w-full">
        <h3 className="text-xl font-bold text-indigo-300 mb-4">
          Admin Area (Secret, desu!) 🤫
        </h3>
        <form onSubmit={handleAdminLogin} className="flex flex-col gap-4">
          <input
            type="password"
            value={adminPassword}
            onChange={(e) => setAdminPassword(e.target.value)}
            placeholder="Enter Mushi's secret password~"
            className="w-full p-3 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Admin password"
          />
          {passwordError && (
            <p className="text-red-400 text-sm mt-1">{passwordError}</p>
          )}
          <button
            type="submit"
            className="w-full px-6 py-3 bg-red-600 text-white font-bold text-lg rounded-full shadow-lg
                       hover:bg-red-700 transform hover:scale-105 transition-all duration-300"
          >
            Access Admin Area (Admin)~
          </button>
        </form>
      </div>

      <footer className="mt-12 text-gray-500 text-sm">
        <p>Powered by the Clank Clank Mushi LLM | 2025 ©</p>
        {/* LLMInfoModal button restored */}
        <div className="mt-2">
          <button
            onClick={() => setIsLLMModalOpen(true)}
            className="text-gray-400 underline hover:text-gray-300"
          >
            What is an LLM?~
          </button>
        </div>
      </footer>

      {/* LLMInfoModal component restored */}
      <LLMInfoModal isOpen={isLLMModalOpen} onClose={() => setIsLLMModalOpen(false)} />
    </div>
  );
}

export default LandingView;
