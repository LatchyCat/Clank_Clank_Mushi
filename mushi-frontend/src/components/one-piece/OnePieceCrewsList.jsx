// mushi-frontend/src/components/one-piece/OnePieceCrewsList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Correct path to api.js

/**
 * OnePieceCrewsList component fetches and displays a list of One Piece crews.
 */
function OnePieceCrewsList() {
  const [crews, setCrews] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCrews = async () => {
      try {
        setIsLoading(true);
        setError(null); // Clear any previous errors
        const data = await api.onePiece.getCrews(); // Fetch One Piece Crews

        if (data) {
          setCrews(data);
          console.log("Mushi found all the amazing One Piece crews for you, Senpai! Waku waku!~ ☆", data);
        } else {
          setError("Muu... Mushi couldn't fetch the One Piece crews. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch One Piece crews:", err);
        setError(`Mushi encountered an error while fetching One Piece crews: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCrews();
  }, []); // Empty dependency array means this effect runs once on mount

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is looking for all the pirate flags for you, Senpai! Kira kira!~ ✨
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-4 border border-red-500 rounded-lg">
        Oh no! {error}
      </div>
    );
  }

  if (!crews || crews.length === 0) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No One Piece crews found. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        One Piece Crews! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {crews.map((crew) => (
          <div key={crew.id} className="bg-gray-800 rounded-lg shadow-lg p-3 text-center transform hover:scale-105 transition-transform duration-300">
            {/* Assuming crew object has 'name' and 'captain' or 'image' */}
            <h3 className="text-white text-md font-semibold truncate mb-1">{crew.name}</h3>
            {crew.captain && <p className="text-gray-400 text-sm">Captain: {crew.captain}</p>}
            {crew.members_count && <p className="text-gray-500 text-xs">Members: {crew.members_count}</p>}
            {/* You could add more details here or link to a detail page if one existed */}
          </div>
        ))}
      </div>
    </div>
  );
}

export default OnePieceCrewsList;
