// mushi-frontend/src/components/anime/AnimeHomeDashboard.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Import your API service

/**
 * AnimeHomeDashboard component fetches and displays various categorized lists of anime
 * for a home or dashboard view, such as spotlights, trending, and schedules.
 */
function AnimeHomeDashboard() {
  const [homeData, setHomeData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        setIsLoading(true);
        setError(null); // Clear any previous errors
        const data = await api.anime.getHomeData();
        if (data) {
          setHomeData(data);
          console.log("Mushi found home data for you, Senpai! ✨", data); // Debugging log
        } else {
          // This case might be hit if handleError in api.js throws, but returns null from catch
          setError("Eeeh~ Mushi couldn't fetch the home anime data, gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch anime home data:", err);
        setError(`Mushi encountered an error while fetching home data: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHomeData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is gathering all the sparkling anime info for you, Senpai! Waku waku!~ ☆
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

  if (!homeData) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... Mushi couldn't find any anime home data. Gomen'nasai! (T_T)
      </div>
    );
  }

  // Helper to render a list of anime (can be further modularized into a Carousel or Grid component)
  const renderAnimeList = (title, list) => {
    if (!list || list.length === 0) {
      return null; // Don't render section if no data
    }
    return (
      <section className="mb-8">
        <h3 className="text-2xl font-bold text-indigo-400 mb-4">{title}</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {list.map((anime) => (
            <div key={anime.id} className="bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300">
              <img
                src={anime.poster_url || 'https://placehold.co/150x220/333/FFF?text=No+Image'}
                alt={anime.title || 'Anime Poster'}
                className="w-full h-auto object-cover rounded-t-lg"
                onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/150x220/333/FFF?text=Image+Error'; }}
              />
              <div className="p-3">
                <h4 className="text-white text-md font-semibold truncate">{anime.title}</h4>
                {anime.show_type && <p className="text-gray-400 text-sm">{anime.show_type}</p>}
                {anime.description && <p className="text-gray-500 text-xs mt-1 line-clamp-2">{anime.description}</p>}
              </div>
            </div>
          ))}
        </div>
      </section>
    );
  };

  const renderScheduleList = (title, list) => {
    if (!list || list.length === 0) {
      return null;
    }
    return (
      <section className="mb-8">
        <h3 className="text-2xl font-bold text-indigo-400 mb-4">{title}</h3>
        <div className="space-y-3">
          {list.map((item) => (
            <div key={item.id} className="bg-gray-800 p-4 rounded-lg shadow-md flex items-center gap-4">
              <div className="flex-shrink-0 text-indigo-300 font-bold text-lg">{item.time}</div>
              <div>
                <h4 className="text-white font-semibold">{item.title}</h4>
                <p className="text-gray-400 text-sm">Episode {item.episode_no} - {item.release_date}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    );
  };

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Welcome to Mushi's Anime Wonderland, Senpai! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>

      {renderAnimeList("Spotlights", homeData.spotlights)}
      {renderAnimeList("Trending Anime", homeData.trending)}
      {renderScheduleList("Today's Schedule", homeData.today_schedule)}
      {renderAnimeList("Top Airing Anime", homeData.top_airing)}
      {renderAnimeList("Most Popular Anime", homeData.most_popular)}
      {renderAnimeList("Most Favorite Anime", homeData.most_favorite)}
      {renderAnimeList("Latest Completed Anime", homeData.latest_completed)}
      {renderAnimeList("Latest Episodes", homeData.latest_episode)}

      {/* You can add more sections or integrate genres here later! */}
      {homeData.genres && homeData.genres.length > 0 && (
        <section className="mb-8">
          <h3 className="text-2xl font-bold text-indigo-400 mb-4">Genres</h3>
          <div className="flex flex-wrap gap-2">
            {homeData.genres.map((genre, index) => (
              <span key={index} className="bg-gray-700 text-gray-300 text-sm px-3 py-1 rounded-full">
                {genre}
              </span>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default AnimeHomeDashboard;
