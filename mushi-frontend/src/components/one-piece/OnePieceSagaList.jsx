// mushi-frontend/src/components/one-piece/OnePieceSagaList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Correct path to api.js

/**
 * OnePieceSagaList component fetches and displays a list of One Piece sagas.
 */
function OnePieceSagaList() {
  const [sagas, setSagas] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSagas = async () => {
      try {
        setIsLoading(true);
        setError(null); // Clear any previous errors
        const data = await api.onePiece.getSagas(); // Fetch One Piece sagas

        if (data) {
          setSagas(data);
          console.log("Mushi found all the grand sagas for you, Senpai! Waku waku!~ ☆", data);
        } else {
          setError("Muu... Mushi couldn't fetch the One Piece sagas. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch One Piece sagas:", err);
        setError(`Mushi encountered an error while fetching One Piece sagas: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSagas();
  }, []); // Empty dependency array means this effect runs once on mount

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is sailing through the Grand Line to find the sagas for you, Senpai! Kira kira!~ ✨
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

  if (!sagas || sagas.length === 0) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No One Piece sagas found. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        One Piece Sagas! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {sagas.map((saga) => (
          <div key={saga.id} className="bg-gray-800 rounded-lg shadow-lg p-6 transform hover:scale-105 transition-transform duration-300">
            <h3 className="text-2xl font-bold text-indigo-400 mb-2">{saga.saga_name}</h3>
            {saga.arcs && saga.arcs.length > 0 && (
              <div className="mt-4">
                <h4 className="text-lg font-semibold text-gray-300 mb-2">Arcs:</h4>
                <ul className="list-disc list-inside text-gray-200">
                  {saga.arcs.map((arc, index) => (
                    <li key={index} className="mb-1">{arc.arc_name} (Episodes: {arc.first_episode}-{arc.last_episode})</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default OnePieceSagaList;
