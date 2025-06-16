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
      <div className="flex justify-center items-center h-60 text-indigo-300 text-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-purple-500/30">
        Mushi is ranking the top anime! Calculating, calculating!~ ヾ(＾-＾)ノ
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

  if (!topTenData || (Object.keys(topTenData).length === 0 && topTenData.constructor === Object)) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg mx-auto max-w-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-gray-700/50">
        Muu... No Top 10 anime data found. (T_T)
      </div>
    );
  }

  // Helper function to render each top 10 list
  const renderTopTenList = (title, list) => {
    if (!list || list.length === 0) return null; // Don't render section if list is empty
    return (
      <section className="mb-10 p-6 bg-white/5 backdrop-blur-md rounded-3xl shadow-2xl border border-white/10">
        <h3 className="text-3xl font-extrabold text-center mb-6
                       bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400
                       drop-shadow-lg [text-shadow:0_0_10px_rgba(255,100,255,0.2)]">
          {title}
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          {list.map((anime) => (
            <div key={anime.id || anime.name} className="bg-gray-800 rounded-xl shadow-lg overflow-hidden
                                                      transform hover:scale-105 transition-transform duration-300
                                                      border border-gray-700 hover:border-indigo-500">
              <img
                src={anime.poster_url || 'https://placehold.co/150x220/333/FFF?text=No+Image'}
                alt={anime.title || anime.name || 'Anime Poster'}
                className="w-full h-auto object-cover rounded-t-xl"
                onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/150x220/333/FFF?text=Image+Error'; }}
              />
              <div className="p-4">
                <h4 className="text-white text-lg font-semibold truncate">{anime.title || anime.name}</h4>
                {anime.show_type && <p className="text-gray-400 text-sm">{anime.show_type}</p>}
                {anime.number && <p className="text-indigo-300 font-bold text-lg mt-1">#{anime.number}</p>}
                {anime.score && (
                  <p className="text-yellow-400 text-sm mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.538 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.783.57-1.838-.197-1.538-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.929 8.72c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z" />
                    </svg>
                    {anime.score.toFixed(2)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    );
  };

  return (
    <div className="p-6 text-gray-100">
      <h2 className="text-4xl font-extrabold text-center mb-10
                     bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-600
                     drop-shadow-lg [text-shadow:0_0_15px_rgba(150,100,255,0.4)]">
        Mushi's Top 10 Anime Lists! 👑
      </h2>

      {renderTopTenList("Top 10 Today", topTenData.today)}
      {renderTopTenList("Top 10 This Week", topTenData.week)}
      {renderTopTenList("Top 10 This Month", topTenData.month)}

      {/* You can add more sections or integrate genres here later! */}
    </div>
  );
}

export default AnimeTopTenList;
