// mushi-frontend/src/components/anime/AnimeHomeDashboard.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Import your API service
import { Link } from 'react-router-dom'; // NEW: Import Link for navigation

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
      <div className="flex justify-center items-center h-48 text-indigo-300 text-lg">
        Mushi is fetching your anime dashboard! Please wait warmly~ (≧∇≦)/
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-6 border border-red-500 rounded-lg bg-red-900 bg-opacity-30 text-lg mx-auto max-w-lg shadow-lg">
        Oh no! {error}
      </div>
    );
  }

  if (!homeData) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg mx-auto max-w-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-gray-700/50">
        Muu... No anime home data found. (T_T)
      </div>
    );
  }

  // Helper function to render common anime lists
  const renderAnimeList = (title, list) => {
    if (!list || list.length === 0) return null;
    return (
      <section className="mb-10 p-6 bg-white/5 backdrop-blur-md rounded-3xl shadow-2xl border border-white/10">
        <h3 className="text-3xl font-extrabold text-center mb-6
                       bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400
                       drop-shadow-lg [text-shadow:0_0_10px_rgba(255,100,255,0.2)]">
          {title}
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          {list.map((anime) => (
            // NEW: Wrap each anime card with a Link to its detail page
            <Link to={`/app/anime/details/${anime.id}`} key={anime.id} className="block bg-gray-800 rounded-xl shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300 border border-gray-700 hover:border-indigo-500">
              <img
                src={anime.poster_url || 'https://placehold.co/150x220/333/FFF?text=No+Image'}
                alt={anime.title}
                className="w-full h-auto object-cover rounded-t-xl"
                onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/150x220/333/FFF?text=Image+Error'; }}
              />
              <div className="p-4">
                <h4 className="text-white text-lg font-semibold truncate mb-1">{anime.title}</h4>
                {anime.show_type && <p className="text-gray-400 text-sm">{anime.show_type}</p>}
                {anime.score && (
                  <p className="text-yellow-400 text-sm mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.538 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.783.57-1.838-.197-1.538-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.929 8.72c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z" />
                    </svg>
                    {anime.score.toFixed(2)}
                  </p>
                )}
              </div>
            </Link>
          ))}
        </div>
      </section>
    );
  };

  // Helper function to render schedule lists
  const renderScheduleList = (title, list) => {
    if (!list || list.length === 0) return null;
    return (
      <section className="mb-10 p-6 bg-white/5 backdrop-blur-md rounded-3xl shadow-2xl border border-white/10">
        <h3 className="text-3xl font-extrabold text-center mb-6
                       bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400
                       drop-shadow-lg [text-shadow:0_0_10px_rgba(255,100,255,0.2)]">
          {title}
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {list.map((item, index) => (
            <div key={item.id || index} className="bg-gray-800 rounded-xl shadow-lg p-4 transform hover:scale-105 transition-transform duration-300 border border-gray-700 hover:border-indigo-500">
              <h4 className="text-white text-lg font-semibold truncate mb-1">{item.title}</h4>
              <p className="text-gray-400 text-sm">Episode: {item.episode_no}</p> {/* Changed from item.episode to item.episode_no */}
              <p className="text-gray-400 text-sm">Release: {item.release_date}</p>
            </div>
          ))}
        </div>
      </section>
    );
  };

  return (
    <div className="p-6 text-gray-100 min-h-screen">
      <h2 className="text-4xl font-extrabold text-center mb-10
                     bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-600
                     drop-shadow-lg [text-shadow:0_0_15px_rgba(150,100,255,0.4)]">
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

      {/* Genres Section - styled similarly to other sections */}
      {homeData.genres && homeData.genres.length > 0 && (
        <section className="mb-10 p-6 bg-white/5 backdrop-blur-md rounded-3xl shadow-2xl border border-white/10">
          <h3 className="text-3xl font-extrabold text-center mb-6
                         bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400
                         drop-shadow-lg [text-shadow:0_0_10px_rgba(255,100,255,0.2)]">
            Explore Genres
          </h3>
          <div className="flex flex-wrap justify-center gap-3">
            {homeData.genres.map((genre, index) => (
              <span key={index} className="bg-purple-700 text-white text-sm font-medium py-2 px-4 rounded-full
                                          hover:bg-purple-600 transition-colors duration-200 cursor-pointer
                                          shadow-md hover:shadow-lg transform hover:scale-105">
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
