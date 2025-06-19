// mushi-frontend/src/components/navigation/FooterNav.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaHeart, FaGithub, FaDiscord } from "react-icons/fa";

// Anime Quote Component (used in 'full' variant)
const AnimeQuote = () => {
  const quotes = [
    { text: "The world isn’t perfect. But it’s there for us, doing the best it can. And that’s what makes it so damn beautiful.", author: "Roy Mustang, Fullmetal Alchemist" },
    { text: "If you don’t take risks, you can’t create a future!", author: "Monkey D. Luffy, One Piece" },
    { text: "To know sorrow is not terrifying. What is terrifying is to know you can't go back to happiness you could have.", author: "Matsumoto Rangiku, Bleach" },
    { text: "People’s lives don’t end when they die. It ends when they lose faith.", author: "Itachi Uchiha, Naruto" },
    { text: "Whatever you lose, you'll find it again. But what you throw away you'll never get back.", author: "Kenshin Himura, Rurouni Kenshin" }
  ];

  const [currentQuote, setCurrentQuote] = useState(quotes[0]);

  useEffect(() => {
    const quoteInterval = setInterval(() => {
      setCurrentQuote(quotes[Math.floor(Math.random() * quotes.length)]);
    }, 15000);
    return () => clearInterval(quoteInterval);
  }, []);

  return (
    <div className="text-center md:text-left">
      <p className="text-lg text-gray-300 italic">"{currentQuote.text}"</p>
      <p className="text-right text-sm text-pink-300 mt-1">- {currentQuote.author}</p>
    </div>
  );
};

// --- NEW COMPONENT FOR THE COMPACT FOOTER ---
const CompactFooter = () => (
    <div className="w-full bg-neutral-900 border-t border-white/10 p-4">
        <div className="container mx-auto flex justify-between items-center text-xs text-gray-500">
            <p>© {new Date().getFullYear()} Clank Clank Mushi. Made with <FaHeart className="inline text-pink-400" /></p>
            <div className="flex items-center gap-4">
                <a href="#" className="hover:text-white" title="Discord"><FaDiscord size={16} /></a>
                <a href="#" className="hover:text-white" title="GitHub"><FaGithub size={16} /></a>
                <Link to="/search" className="hover:text-white">Search</Link>
                <Link to="/az-list" className="hover:text-white">A-Z List</Link>
            </div>
        </div>
    </div>
);


// Main Footer Component (Now accepts a 'variant' prop)
function FooterNav({ images, currentIndex, variant = 'full' }) {
    const websiteName = "Clank Clank Mushi";

    if (variant === 'compact') {
        return <CompactFooter />;
    }

    // CSS for the panning animation
    const panAnimation = `
        @keyframes pan-image {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
    `;

    return (
        <footer className="relative w-full mt-[100px] p-8 overflow-hidden">
            <style>{panAnimation}</style>

            {/* Panning Background */}
            <div
                className="absolute inset-0 w-full h-full transition-opacity duration-1000"
                style={{
                    backgroundImage: `url(${images[currentIndex]})`,
                    backgroundSize: '150% auto', // Zoom in slightly to allow for panning
                    animation: 'pan-image 30s linear infinite',
                    willChange: 'background-position',
                }}
            />

            {/* Overlay to ensure text readability */}
            <div className="absolute inset-0 bg-neutral-900/80 backdrop-blur-sm z-0"></div>

            <div className="relative z-10 container mx-auto grid grid-cols-1 md:grid-cols-12 gap-8 text-white">

                {/* Left Side: Logo and Quote */}
                <div className="md:col-span-5 space-y-6">
                    <h2 className="text-3xl font-extrabold text-white">Clank Clank Mushi</h2>
                    <AnimeQuote />
                </div>

                {/* Center: Quick Links */}
                <div className="md:col-span-4">
                    <h3 className="font-bold text-lg text-pink-300 uppercase tracking-wider mb-4">Explore</h3>
                    <div className="grid grid-cols-2 gap-2">
                        <Link to="/home" className="hover:text-white">Home</Link>
                        <Link to="/search" className="hover:text-white">Anime Search</Link>
                        <Link to="/search?category=top-airing&title=Top Airing" className="hover:text-white">Top Airing</Link>
                        <Link to="/search?category=most-popular&title=Most Popular" className="hover:text-white">Most Popular</Link>
                        <Link to="/az-list" className="hover:text-white">A-Z List</Link>
                        <Link to="/mushi_ai" className="hover:text-white">Ask Mushi AI</Link>
                    </div>
                </div>

                {/* Right Side: Character Spotlight */}
                <div className="md:col-span-3">
                     <h3 className="font-bold text-lg text-pink-300 uppercase tracking-wider mb-4">Character Spotlight</h3>
                     <div className="bg-white/10 rounded-lg p-3 flex items-center gap-4">
                        <img src="/mushi_snail_zoro.png" alt="Zoro" className="w-16 h-16 object-contain rounded-full bg-neutral-900 p-1" />
                        <div>
                            <h4 className="font-semibold">Roronoa Zoro</h4>
                            <p className="text-xs text-gray-400">Did you know? Zoro was originally intended to be Buggy the Clown's bodyguard!</p>
                        </div>
                     </div>
                </div>

                {/* Bottom Bar: Copyright & Social */}
                <div className="md:col-span-12 mt-8 pt-6 border-t border-white/10 flex flex-col md:flex-row justify-between items-center text-sm text-gray-400 gap-4">
                     <p>Powered by the Mushi LLM | © {new Date().getFullYear()} {websiteName}. Made with <FaHeart className="inline text-pink-400" /></p>
                     <p>{websiteName} does not host any files on our server, we only link to media hosted on 3rd party services.</p>
                </div>

            </div>
        </footer>
    );
}

export default FooterNav;
