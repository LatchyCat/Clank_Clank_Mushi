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
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is looking for what's super popular to search, desu! Waku waku!~ ☆
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

  if (!topSearchData || topSearchData.length === 0) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... Mushi couldn't find any Top Search anime data. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Mushi's Popular Search Picks! ✨
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {topSearchData.map((item, index) => (
          <div key={index} className="bg-gray-800 rounded-lg shadow-lg p-4 transform hover:scale-105 transition-transform duration-300">
            {/* Assuming 'title' and 'link' are available for each item */}
            <h3 className="text-white text-lg font-semibold truncate">{item.title}</h3>
            {item.link && (
              <a
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-400 hover:text-indigo-300 text-sm mt-1 inline-block"
              >
                View Details~
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AnimeTopSearchList;
