// mushi-frontend/src/components/anime/characters/CharacterDetailViewer.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../../services/api'; // Correct path to api.js
import { Link } from 'react-router-dom'; // For linking to anime details

/**
 * CharacterDetailViewer component fetches and displays comprehensive details for a specific anime character.
 * It takes the character ID as a prop.
 *
 * @param {object} props
 * @param {string} props.characterId - The ID of the character to display details for.
 */
function CharacterDetailViewer({ characterId }) {
  const [characterDetails, setCharacterDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      if (!characterId) {
        setError("Eeeh~ Senpai, Mushi needs a Character ID to show details! (•́-•̀)");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null); // Clear previous errors
        const data = await api.anime.getCharacterDetails(characterId); // Fetch character details

        if (data) {
          setCharacterDetails(data);
          console.log(`Mushi found all the sparkling details for Character ID: ${characterId}, desu!~`, data);
        } else {
          setError("Muu... Mushi couldn't find details for that character. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error(`Uwaah! Failed to fetch details for character ID ${characterId}:`, err);
        setError(`Mushi encountered an error while fetching character details: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetails();
  }, [characterId]); // Re-run effect when characterId changes

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is drawing all the adorable character info for you, Senpai! Waku waku!~ ☆
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

  if (!characterDetails) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No details found for this character. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        {characterDetails.name} Details! ☆
      </h2>

      <div className="max-w-4xl mx-auto bg-gray-800 rounded-lg shadow-xl p-6 md:flex md:space-x-6">
        <div className="md:w-1/3 flex-shrink-0">
          <img
            src={characterDetails.profile_url || 'https://placehold.co/300x450/333/FFF?text=No+Image'}
            alt={characterDetails.name || 'Character Profile'}
            className="w-full h-auto object-cover rounded-lg shadow-md"
            onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/300x450/333/FFF?text=Image+Error'; }}
          />
        </div>
        <div className="md:w-2/3 mt-6 md:mt-0">
          <h3 className="text-2xl font-bold text-indigo-400 mb-2">{characterDetails.name}</h3>
          {characterDetails.japanese_name && <p className="text-gray-400 italic mb-4">{characterDetails.japanese_name}</p>}

          <h4 className="text-lg font-semibold text-indigo-300 mb-2">About:</h4>
          <p className="text-gray-200 leading-relaxed mb-4" dangerouslySetInnerHTML={{ __html: characterDetails.about_description || "No description available, gomen'nasai!" }}></p>

          {/* Voice Actors Section */}
          {characterDetails.voice_actors && characterDetails.voice_actors.length > 0 && (
            <section className="mb-6">
              <h4 className="text-lg font-semibold text-indigo-300 mb-2">Voice Actors:</h4>
              <div className="grid grid-cols-2 gap-4">
                {characterDetails.voice_actors.map((va) => (
                  <div key={va.id} className="bg-gray-700 rounded-lg shadow-md p-3 flex items-center space-x-3">
                    <img
                      src={va.profile_url || 'https://placehold.co/60x60/555/EEE?text=VA'}
                      alt={va.name || 'Voice Actor'}
                      className="w-16 h-16 rounded-full object-cover flex-shrink-0"
                      onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/60x60/555/EEE?text=VA'; }}
                    />
                    <div>
                      <h5 className="text-white font-semibold">{va.name}</h5>
                      <p className="text-gray-400 text-sm">{va.language}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Animeography Section */}
          {characterDetails.animeography && characterDetails.animeography.length > 0 && (
            <section>
              <h4 className="text-lg font-semibold text-indigo-300 mb-2">Animeography:</h4>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                {characterDetails.animeography.map((anime) => (
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
        </div>
      </div>
    </div>
  );
}

export default CharacterDetailViewer;
