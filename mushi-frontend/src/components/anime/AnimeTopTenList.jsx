// mushi-frontend/src/components/anime/AnimeTopTenList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Import your API service

/**
 * AnimeTopTenList component fetches and displays the top 10 anime for today,
 * this week, and this month from the backend.
 */
function AnimeTopTenList() {
  const [topTenData, setTopTenData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTopTenData = async () => {
      try {
        setIsLoading(true);
        setError(null); // Clear any previous errors
        const data = await api.anime.getTopTen(); // Call the API to get top ten data
        if (data) {
          setTopTenData(data);
          console.log("Mushi fetched the sparkling Top 10 lists for you, Senpai! (ﾉ´ヮ´)ﾉ*:･ﾟ✧", data); // Debugging log
        } else {
          setError("Eeeh~ Mushi couldn't fetch the Top 10 anime data, gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch Top 10 anime data:", err);
        setError(`Mushi encountered an error while fetching Top 10 data: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTopTenData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is counting all the most popular anime for you, Senpai! Waku waku!~ ☆
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

  if (!topTenData || (Object.keys(topTenData).length === 0 && topTenData.constructor === Object)) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... Mushi couldn't find any Top 10 anime data. (T_T)
      </div>
    );
  }

  // Helper to render a list of anime (can be further modularized)
  const renderAnimeList = (title, list) => {
    if (!list || list.length === 0) {
      return null; // Don't render section if no data
    }
    return (
      <section className="mb-8">
        <h3 className="text-2xl font-bold text-indigo-400 mb-4">{title}</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {list.map((anime) => (
            <div key={anime.id || anime.name} className="bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300">
              <img
                src={anime.poster_url || 'https://placehold.co/150x220/333/FFF?text=No+Image'}
                alt={anime.title || anime.name || 'Anime Poster'}
                className="w-full h-auto object-cover rounded-t-lg"
                onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/150x220/333/FFF?text=Image+Error'; }}
              />
              <div className="p-3">
                <h4 className="text-white text-md font-semibold truncate">{anime.title || anime.name}</h4>
                {anime.show_type && <p className="text-gray-400 text-sm">{anime.show_type}</p>}
                {anime.number && <p className="text-indigo-300 font-bold text-sm">#{anime.number}</p>}
              </div>
            </div>
          ))}
        </div>
      </section>
    );
  };

  return (
    <div className="p-6 bg-gray-900 text-gray-100">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Mushi's Top 10 Anime Picks! (≧∇≦)ﾉ
      </h2>

      {renderAnimeList("Top 10 Today", topTenData.today)}
      {renderAnimeList("Top 10 This Week", topTenData.week)}
      {renderAnimeList("Top 10 This Month", topTenData.month)}
    </div>
  );
}

export default AnimeTopTenList;
