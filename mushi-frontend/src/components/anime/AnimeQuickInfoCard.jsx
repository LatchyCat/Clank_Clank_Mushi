// mushi-frontend/src/components/anime/AnimeQuickInfoCard.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Correct path to api.js

/**
 * AnimeQuickInfoCard component fetches and displays a "quick tip" or brief information
 * about a specific anime based on its qtipId.
 *
 * @param {object} props
 * @param {number} props.qtipId - The ID of the Qtip/quick info to display.
 */
function AnimeQuickInfoCard({ qtipId }) {
  const [qtipInfo, setQtipInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQtip = async () => {
      if (!qtipId) {
        setError("Eeeh~ Senpai, Mushi needs a Qtip ID to show quick info! (•́-•̀)");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null); // Clear previous errors
        const data = await api.anime.getQtipInfo(qtipId); // Fetch Qtip info

        if (data) {
          setQtipInfo(data);
          console.log(`Mushi found quick info for Qtip ID: ${qtipId}, desu!~`, data);
        } else {
          setError("Muu... Mushi couldn't find quick info for that ID. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error(`Uwaah! Failed to fetch Qtip info for ID ${qtipId}:`, err);
        setError(`Mushi encountered an error while fetching quick info: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchQtip();
  }, [qtipId]); // Re-run effect when qtipId changes

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-24 text-indigo-300 text-sm
                      bg-white/5 backdrop-blur-sm rounded-xl shadow-inner border border-purple-500/30">
        Mushi is thinking of a quick tip! Waku waku!~ ☆
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-4 border border-red-500 rounded-xl bg-red-900/30 text-sm shadow-md">
        Oh no! {error}
      </div>
    );
  }

  if (!qtipInfo) {
    return (
      <div className="text-gray-400 text-center p-4 text-sm
                      bg-white/5 backdrop-blur-sm rounded-xl shadow-inner border border-gray-700/50">
        Muu... No quick info found. (T_T)
      </div>
    );
  }

  return (
    <div className="bg-white/5 backdrop-blur-md rounded-xl shadow-2xl p-6 text-gray-100 border border-purple-500/30
                    transform hover:scale-[1.02] transition-transform duration-300 hover:shadow-purple-500/20">
      <h3 className="text-2xl font-bold mb-3
                     bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400
                     drop-shadow-lg [text-shadow:0_0_8px_rgba(255,100,255,0.2)]">
        {qtipInfo.title || "Quick Info"}
      </h3>
      <p className="text-gray-200 text-base leading-relaxed mb-4">{qtipInfo.description || "No description provided."}</p>

      {/* Optional: Add a link or button for more details */}
      {qtipInfo.link && (
        <a
          href={qtipInfo.link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center text-indigo-400 hover:text-indigo-300 text-sm font-medium
                     bg-purple-800/50 px-4 py-2 rounded-full transition-all duration-200
                     hover:bg-purple-700/70 shadow-md hover:shadow-lg"
        >
          Learn More~
          <svg xmlns="http://www.w3.org/2000/svg" className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </a>
      )}
    </div>
  );
}

export default AnimeQuickInfoCard;
