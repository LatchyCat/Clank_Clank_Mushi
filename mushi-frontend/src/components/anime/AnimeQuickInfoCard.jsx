// mushi-frontend/src/components/anime/AnimeQuickInfoCard.jsx
import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';

function AnimeQuickInfoCard({ qtipId }) {
  const [qtipInfo, setQtipInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  // --- START OF DEFINITIVE FIX ---
  // Use a ref to track the last ID we fetched to prevent unnecessary state resets
  const fetchedIdRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    const fetchQtip = async () => {
      if (!qtipId) {
        if (isMounted) setIsLoading(false);
        return;
      }

      // ONLY reset state and show loader if we are fetching for a NEW anime ID.
      // This prevents the flicker when the parent component re-renders for other reasons (like position updates).
      if (qtipId !== fetchedIdRef.current) {
        if (isMounted) {
            setIsLoading(true);
            setError(null);
            setQtipInfo(null);
        }
        fetchedIdRef.current = qtipId; // Mark this ID as being fetched
      } else {
        // If it's the same ID, we don't need to re-show the loader or clear existing data.
        // This makes the card feel stable even during parent re-renders.
        if(isMounted) setIsLoading(false);
      }


      try {
        const data = await api.anime.getQtipInfo(qtipId);

        if (isMounted) {
          if (data && data.title) {
            setQtipInfo(data);
          } else {
            setQtipInfo(null);
            console.warn(`Qtip for ID ${qtipId} returned no valid data.`);
          }
        }
      } catch (err) {
        if (isMounted) {
          console.error(`Uwaah! Failed to fetch Qtip info for ID ${qtipId}:`, err);
          setError(`Mushi couldn't get quick info. Gomen!`);
          setQtipInfo(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchQtip();

    return () => {
      isMounted = false;
    };
  }, [qtipId]);
  // --- END OF DEFINITIVE FIX ---


  // Show loader only when loading is true AND we don't have previous info to display
  if (isLoading && !qtipInfo) {
    return (
      <div className="w-80 p-4 bg-neutral-800 rounded-lg shadow-xl text-center text-indigo-300 text-sm animate-pulse">
        Mushi is peeking...
      </div>
    );
  }

  // If there's an error, or if there's no data after loading, render nothing.
  if (error || !qtipInfo) {
    return null;
  }

  // Otherwise, render the card with the fetched data.
  return (
    <div className="w-80 bg-neutral-900 border border-purple-500/30 backdrop-blur-md rounded-xl shadow-2xl p-6 text-gray-100 transform transition-transform duration-300">
      <h3 className="text-xl font-bold mb-3
                     bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400
                     drop-shadow-lg [text-shadow:0_0_8px_rgba(255,100,255,0.2)] line-clamp-2">
        {qtipInfo.title}
      </h3>
      <p className="text-gray-300 text-sm leading-relaxed mb-4 line-clamp-4">{qtipInfo.description || "No description provided."}</p>

      <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs text-gray-400">
        <span><strong className="text-gray-200">Type:</strong> {qtipInfo.type || 'N/A'}</span>
        <span><strong className="text-gray-200">Episodes:</strong> {qtipInfo.episodeCount || 'N/A'}</span>
        <span><strong className="text-gray-200">Status:</strong> {qtipInfo.status || 'N/A'}</span>
        <span><strong className="text-gray-200">Rating:</strong> {qtipInfo.rating || 'N/A'}</span>
      </div>
    </div>
  );
}

export default AnimeQuickInfoCard;
