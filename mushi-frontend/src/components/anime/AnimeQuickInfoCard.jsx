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
      <div className="flex justify-center items-center h-24 text-indigo-300 text-sm">
        Mushi is thinking of a quick tip! Waku waku!~ ☆
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-2 border border-red-500 rounded-lg text-sm">
        Oh no! {error}
      </div>
    );
  }

  if (!qtipInfo) {
    return (
      <div className="text-gray-400 text-center p-2 text-sm">
        Muu... No quick info found. (T_T)
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-4 text-gray-100 border border-indigo-600">
      <h3 className="text-xl font-bold text-indigo-400 mb-2">{qtipInfo.title || "Quick Info"}</h3>
      <p className="text-gray-200 text-base leading-relaxed">{qtipInfo.description || "No description provided."}</p>
      {qtipInfo.mal_link && (
        <a
          href={qtipInfo.mal_link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-300 hover:text-indigo-200 text-sm mt-3 inline-block"
        >
          Read more on MyAnimeList~
        </a>
      )}
    </div>
  );
}

export default AnimeQuickInfoCard;
