// mushi-frontend/src/components/anime/details/AnimeDetailViewer.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../../services/api'; // Correct path to api.js

/**
 * AnimeDetailViewer component fetches and displays comprehensive details for a specific anime.
 * It takes the anime ID as a prop.
 *
 * @param {object} props
 * @param {string} props.animeId - The ID of the anime to display details for.
 */
function AnimeDetailViewer({ animeId }) {
  const [animeDetails, setAnimeDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      if (!animeId) {
        setError("Eeeh~ Senpai, Mushi needs an Anime ID to show details! (•́-•̀)");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null); // Clear previous errors
        const data = await api.anime.getDetails(animeId); // Fetch anime details

        if (data) {
          setAnimeDetails(data);
          console.log(`Mushi found all the sparkling details for Anime ID: ${animeId}, desu!~`, data);
        } else {
          setError("Muu... Mushi couldn't find details for that anime. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error(`Uwaah! Failed to fetch details for anime ID ${animeId}:`, err);
        setError(`Mushi encountered an error while fetching anime details: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetails();
  }, [animeId]); // Re-run effect when animeId changes

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is gathering all the secrets for this anime, Senpai! Waku waku!~ ☆
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

  if (!animeDetails) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No details found for this anime. (T_T)
      </div>
    );
  }

  // Helper to render a list of genres or producers
  const renderTags = (title, tags) => {
    if (!tags || tags.length === 0) return null;
    return (
      <div>
        <h4 className="text-lg font-semibold text-indigo-300 mb-2">{title}:</h4>
        <div className="flex flex-wrap gap-2 mb-4">
          {tags.map((tag, index) => (
            <span key={index} className="bg-gray-700 text-gray-300 text-sm px-3 py-1 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      </div>
    );
  };

  // Helper to render lists of related/recommended anime
  const renderRelatedAnime = (title, list) => {
    if (!list || list.length === 0) return null;
    return (
      <section className="mb-8">
        <h3 className="text-2xl font-bold text-indigo-400 mb-4">{title}</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
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
        {animeDetails.title} Details! ☆
      </h2>

      <div className="max-w-4xl mx-auto bg-gray-800 rounded-lg shadow-xl p-6 md:flex md:space-x-6">
        <div className="md:w-1/3 flex-shrink-0">
          <img
            src={animeDetails.poster_url || 'https://placehold.co/300x450/333/FFF?text=No+Poster'}
            alt={animeDetails.title || 'Anime Poster'}
            className="w-full h-auto object-cover rounded-lg shadow-md"
            onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/300x450/333/FFF?text=Image+Error'; }}
          />
        </div>
        <div className="md:w-2/3 mt-6 md:mt-0">
          <h3 className="text-2xl font-bold text-indigo-400 mb-2">{animeDetails.title}</h3>
          {animeDetails.japanese_title && <p className="text-gray-400 italic mb-2">{animeDetails.japanese_title}</p>}
          {animeDetails.show_type && <p className="text-gray-300 text-sm mb-1">Type: {animeDetails.show_type}</p>}
          {animeDetails.status && <p className="text-gray-300 text-sm mb-1">Status: {animeDetails.status}</p>}
          {animeDetails.aired && <p className="text-gray-300 text-sm mb-1">Aired: {animeDetails.aired}</p>}
          {animeDetails.mal_score && <p className="text-gray-300 text-sm mb-4">MAL Score: <span className="text-yellow-400 font-bold">{animeDetails.mal_score}</span></p>}

          <h4 className="text-lg font-semibold text-indigo-300 mb-2">Overview:</h4>
          <p className="text-gray-200 leading-relaxed mb-4">{animeDetails.overview || "No overview available, gomen'nasai!"}</p>

          {renderTags("Genres", animeDetails.genres)}
          {renderTags("Studios", animeDetails.studios)}
          {renderTags("Producers", animeDetails.producers)}

          {/* Characters and Voice Actors Section */}
          {animeDetails.characters_voice_actors && animeDetails.characters_voice_actors.length > 0 && (
            <section className="mb-8">
              <h3 className="text-2xl font-bold text-indigo-400 mb-4">Characters & Voice Actors</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {animeDetails.characters_voice_actors.map((charInfo) => (
                  <div key={charInfo.character_id} className="bg-gray-700 rounded-lg shadow-md p-3 text-center">
                    <img
                      src={charInfo.character_poster_url || 'https://placehold.co/80x80/555/EEE?text=Char'}
                      alt={charInfo.character_name || 'Character'}
                      className="w-20 h-20 rounded-full object-cover mx-auto mb-2"
                      onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/80x80/555/EEE?text=Char'; }}
                    />
                    <h5 className="text-white text-sm font-semibold truncate">{charInfo.character_name}</h5>
                    {charInfo.voice_actors && charInfo.voice_actors.length > 0 && (
                      <div className="text-gray-400 text-xs mt-1">
                        {charInfo.voice_actors.map((va, idx) => (
                          <p key={idx} className="truncate">{va.name} (VA)</p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Seasons Section */}
          {animeDetails.seasons && animeDetails.seasons.length > 0 && (
            <section className="mb-8">
              <h3 className="text-2xl font-bold text-indigo-400 mb-4">Seasons</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {animeDetails.seasons.map((season) => (
                  <div key={season.id} className="bg-gray-700 rounded-lg shadow-md overflow-hidden">
                    <img
                      src={season.season_poster_url || 'https://placehold.co/100x150/555/EEE?text=Season'}
                      alt={season.title || 'Season'}
                      className="w-full h-auto object-cover"
                      onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/100x150/555/EEE?text=Season'; }}
                    />
                    <div className="p-2 text-center">
                      <h5 className="text-white text-sm font-semibold">{season.season_name}</h5>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>

      {renderRelatedAnime("Related Anime", animeDetails.related_anime)}
      {renderRelatedAnime("Recommended Anime", animeDetails.recommended_anime)}
    </div>
  );
}

export default AnimeDetailViewer;
