// mushi-frontend/src/components/anime/actors/VoiceActorDetailViewer.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../../services/api'; // Correct path to api.js
import { Link } from 'react-router-dom'; // For linking to anime details

/**
 * VoiceActorDetailViewer component fetches and displays comprehensive details for a specific voice actor.
 * It takes the actor ID as a prop.
 *
 * @param {object} props
 * @param {string} props.actorId - The ID of the voice actor to display details for.
 */
function VoiceActorDetailViewer({ actorId }) {
  const [actorDetails, setActorDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      if (!actorId) {
        setError("Eeeh~ Senpai, Mushi needs an Actor ID to show details! (•́-•̀)");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null); // Clear previous errors
        const data = await api.anime.getVoiceActorDetails(actorId); // Fetch voice actor details

        if (data) {
          setActorDetails(data);
          console.log(`Mushi found all the sparkling details for Voice Actor ID: ${actorId}, desu!~`, data);
        } else {
          setError("Muu... Mushi couldn't find details for that voice actor. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error(`Uwaah! Failed to fetch details for voice actor ID ${actorId}:`, err);
        setError(`Mushi encountered an error while fetching voice actor details: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetails();
  }, [actorId]); // Re-run effect when actorId changes

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is listening carefully for all the voice actor info for you, Senpai! Waku waku!~ ☆
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

  if (!actorDetails) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No details found for this voice actor. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        {actorDetails.name} Details! ☆
      </h2>

      <div className="max-w-4xl mx-auto bg-gray-800 rounded-lg shadow-xl p-6 md:flex md:space-x-6">
        <div className="md:w-1/3 flex-shrink-0">
          <img
            src={actorDetails.profile_url || 'https://placehold.co/300x450/333/FFF?text=No+Image'}
            alt={actorDetails.name || 'Voice Actor Profile'}
            className="w-full h-auto object-cover rounded-lg shadow-md"
            onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/300x450/333/FFF?text=Image+Error'; }}
          />
        </div>
        <div className="md:w-2/3 mt-6 md:mt-0">
          <h3 className="text-2xl font-bold text-indigo-400 mb-2">{actorDetails.name}</h3>
          {actorDetails.japanese_name && <p className="text-gray-400 italic mb-2">{actorDetails.japanese_name}</p>}
          {actorDetails.language && <p className="text-gray-300 text-sm mb-4">Language: {actorDetails.language}</p>}

          <h4 className="text-lg font-semibold text-indigo-300 mb-2">About:</h4>
          <p className="text-gray-200 leading-relaxed mb-4" dangerouslySetInnerHTML={{ __html: actorDetails.about_description || "No description available, gomen'nasai!" }}></p>

          {/* Animeography Section */}
          {actorDetails.animeography && actorDetails.animeography.length > 0 && (
            <section>
              <h4 className="text-lg font-semibold text-indigo-300 mb-2">Animeography:</h4>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                {actorDetails.animeography.map((anime) => (
                  <Link to={`/app/anime/details/${anime.id}`} key={anime.id} className="block bg-gray-700 rounded-lg shadow-md overflow-hidden transform hover:scale-105 transition-transform duration-300">
                    <img
                      src={anime.poster_url || 'https://placehold.co/80x120/444/CCC?text=Anime'}
                      alt={anime.title || 'Anime'}
                      className="w-full h-auto object-cover"
                      onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/80x120/444/CCC?text=Anime'; }}
                    />
                    <div className="p-2 text-center">
                      <h5 className="text-white text-xs font-semibold line-clamp-2">{anime.title}</h5>
                      <p className="text-gray-400 text-xs mt-1">{anime.role}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Characters Voiced Section */}
          {actorDetails.characters_voiced && actorDetails.characters_voiced.length > 0 && (
            <section className="mt-8">
              <h4 className="text-lg font-semibold text-indigo-300 mb-2">Characters Voiced:</h4>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                {actorDetails.characters_voiced.map((char) => (
                  <Link to={`/app/anime/character/${char.id}`} key={char.id} className="block bg-gray-700 rounded-lg shadow-md overflow-hidden transform hover:scale-105 transition-transform duration-300">
                    <img
                      src={char.poster_url || 'https://placehold.co/80x80/555/EEE?text=Char'}
                      alt={char.name || 'Character'}
                      className="w-full h-auto object-cover rounded-t-lg"
                      onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/80x80/555/EEE?text=Char'; }}
                    />
                    <div className="p-2 text-center">
                      <h5 className="text-white text-xs font-semibold line-clamp-2">{char.name}</h5>
                      <p className="text-gray-400 text-xs mt-1">{char.anime_title}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

export default VoiceActorDetailViewer;
