// mushi-frontend/src/components/anime/AnimeTopSearchList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Import your API service

/**
 * AnimeTopSearchList component fetches and displays a list of top searched anime
 * or popular search terms from the backend.
 */
function AnimeTopSearchList() {
  const [topSearchData, setTopSearchData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTopSearchData = async () => {
      try {
        setIsLoading(true);
        setError(null); // Clear any previous errors
        // You can specify a limit here if desired, e.g., api.anime.getTopSearch(10)
        const data = await api.anime.getTopSearch();
        if (data && data.results) { // Ensure 'results' key exists from backend
          setTopSearchData(data.results);
          console.log("Mushi found the top searches for you, Senpai! Hehe~", data.results); // Debugging log
        } else {
          setError("Eeeh~ Mushi couldn't fetch the Top Search anime data, gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch Top Search anime data:", err);
        setError(`Mushi encountered an error while fetching Top Search data: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTopSearchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-48 text-indigo-300 text-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-purple-500/30">
        Mushi is fetching the most popular searches! Searching, searching!~ ☆
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-6 border border-red-500 rounded-lg bg-red-900/30 text-lg mx-auto max-w-lg shadow-lg">
        Oh no! {error}
      </div>
    );
  }

  if (!topSearchData || topSearchData.length === 0) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg mx-auto max-w-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-gray-700/50">
        Muu... Mushi couldn't find any Top Search anime data. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 text-gray-100">
      <h2 className="text-4xl font-extrabold text-center mb-10
                     bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-600
                     drop-shadow-lg [text-shadow:0_0_15px_rgba(150,100,255,0.4)]">
        Mushi's Popular Search Picks! ✨
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {topSearchData.map((item, index) => (
          <div key={index} className="bg-white/5 backdrop-blur-md rounded-xl shadow-lg p-5
                                      transform hover:scale-105 transition-transform duration-300
                                      border border-white/10 hover:border-indigo-500">
            {/* Assuming 'title' and 'link' are available for each item */}
            <h3 className="text-white text-xl font-semibold truncate mb-2">
              {item.title}
            </h3>
            {item.link && (
              <a
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-indigo-400 hover:text-indigo-300 text-sm font-medium
                           bg-purple-800/50 px-4 py-2 rounded-full transition-all duration-200
                           hover:bg-purple-700/70 shadow-md hover:shadow-lg"
              >
                View Details~
                <svg xmlns="http://www.w3.org/2000/svg" className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AnimeTopSearchList;
