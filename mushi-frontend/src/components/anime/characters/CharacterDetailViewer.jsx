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
      <div className="flex justify-center items-center h-screen-75 text-indigo-300 text-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-purple-500/30">
        Mushi is gathering character details! Please wait warmly~ (≧∇≦)/
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

  if (!characterDetails) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg mx-auto max-w-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-gray-700/50">
        Muu... No character details found. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 text-gray-100 min-h-screen">
      <div className="bg-white/5 backdrop-blur-md rounded-3xl shadow-2xl p-8 border border-white/10">
        <h2 className="text-4xl font-extrabold text-center mb-8
                       bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-600
                       drop-shadow-lg [text-shadow:0_0_15px_rgba(150,100,255,0.4)]">
          {characterDetails.name} <span className="text-purple-400 text-xl">({characterDetails.japanese_name})</span>
        </h2>

        <div className="flex flex-col md:flex-row gap-8 mb-8 items-start">
          {/* Character Image */}
          <div className="flex-shrink-0 w-full md:w-1/3 lg:w-1/4">
            <img
              src={characterDetails.image_url || 'https://placehold.co/300x450/333/FFF?text=Character+Image'}
              alt={characterDetails.name}
              className="w-full h-auto object-cover rounded-2xl shadow-xl border-4 border-indigo-600/50"
              onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/300x450/333/FFF?text=Image+Error'; }}
            />
          </div>

          {/* Character Info */}
          <div className="flex-grow">
            <p className="text-gray-300 text-base leading-relaxed mb-6 whitespace-pre-wrap">
              {characterDetails.description || "No description available. Gomen'nasai!"}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-lg">
              {characterDetails.anime_debut && (
                <p className="text-purple-300"><strong className="text-white">Anime Debut:</strong> {characterDetails.anime_debut}</p>
              )}
              {characterDetails.manga_debut && (
                <p className="text-purple-300"><strong className="text-white">Manga Debut:</strong> {characterDetails.manga_debut}</p>
              )}
              {characterDetails.birth_date && (
                <p className="text-purple-300"><strong className="text-white">Birthday:</strong> {characterDetails.birth_date}</p>
              )}
              {characterDetails.age && (
                <p className="text-purple-300"><strong className="text-white">Age:</strong> {characterDetails.age}</p>
              )}
              {characterDetails.gender && (
                <p className="text-purple-300"><strong className="text-white">Gender:</strong> {characterDetails.gender}</p>
              )}
              {characterDetails.height && (
                <p className="text-purple-300"><strong className="text-white">Height:</strong> {characterDetails.height}</p>
              )}
              {characterDetails.weight && (
                <p className="text-purple-300"><strong className="text-white">Weight:</strong> {characterDetails.weight}</p>
              )}
              {characterDetails.blood_type && (
                <p className="text-purple-300"><strong className="text-white">Blood Type:</strong> {characterDetails.blood_type}</p>
              )}
            </div>
          </div>
        </div>

        {/* Voice Actors Section */}
        {characterDetails.voice_actors && characterDetails.voice_actors.length > 0 && (
          <section className="mb-8 p-6 bg-white/5 rounded-2xl border border-white/10 shadow-inner">
            <h3 className="text-2xl font-bold mb-4
                           bg-clip-text text-transparent bg-gradient-to-r from-pink-300 to-purple-300
                           drop-shadow-lg [text-shadow:0_0_8px_rgba(255,100,255,0.1)]">
              Voice Actors
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {characterDetails.voice_actors.map((actor) => (
                <Link to={`/app/anime/voice_actor/${actor.id}`} key={actor.id} className="block bg-gray-800 rounded-xl shadow-md overflow-hidden
                                                                                              transform hover:scale-105 transition-transform duration-300
                                                                                              border border-gray-700 hover:border-purple-500">
                  <img
                    src={actor.image_url || 'https://placehold.co/100x100/444/CCC?text=VA'}
                    alt={actor.name}
                    className="w-full h-auto object-cover rounded-t-xl"
                    onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/100x100/444/CCC?text=VA'; }}
                  />
                  <div className="p-3 text-center">
                    <h4 className="text-white text-md font-semibold line-clamp-2">{actor.name}</h4>
                    <p className="text-gray-400 text-sm">{actor.language}</p>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Animeography Section */}
        {characterDetails.animeography && characterDetails.animeography.length > 0 && (
          <section className="mb-8 p-6 bg-white/5 rounded-2xl border border-white/10 shadow-inner">
            <h3 className="text-2xl font-bold mb-4
                           bg-clip-text text-transparent bg-gradient-to-r from-pink-300 to-purple-300
                           drop-shadow-lg [text-shadow:0_0_8px_rgba(255,100,255,0.1)]">
              Animeography
            </h3>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
              {characterDetails.animeography.map((anime) => (
                <Link to={`/app/anime/details/${anime.id}`} key={anime.id} className="block bg-gray-800 rounded-xl shadow-md overflow-hidden
                                                                                           transform hover:scale-105 transition-transform duration-300
                                                                                           border border-gray-700 hover:border-purple-500">
                  <img
                    src={anime.poster_url || 'https://placehold.co/80x120/444/CCC?text=Anime'}
                    alt={anime.title || 'Anime'}
                    className="w-full h-auto object-cover rounded-t-xl"
                    onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/80x120/444/CCC?text=Anime'; }}
                  />
                  <div className="p-3 text-center">
                    <h5 className="text-white text-sm font-semibold line-clamp-2">{anime.title}</h5>
                    <p className="text-gray-400 text-xs mt-1">{anime.role}</p>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Mangaography Section (if applicable) */}
        {characterDetails.mangaography && characterDetails.mangaography.length > 0 && (
          <section className="mb-8 p-6 bg-white/5 rounded-2xl border border-white/10 shadow-inner">
            <h3 className="text-2xl font-bold mb-4
                           bg-clip-text text-transparent bg-gradient-to-r from-pink-300 to-purple-300
                           drop-shadow-lg [text-shadow:0_0_8px_rgba(255,100,255,0.1)]">
              Mangaography
            </h3>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
              {characterDetails.mangaography.map((manga) => (
                <div key={manga.id} className="block bg-gray-800 rounded-xl shadow-md overflow-hidden
                                              transform hover:scale-105 transition-transform duration-300
                                              border border-gray-700 hover:border-purple-500">
                  {/* Assuming manga also has a poster_url and title */}
                  <img
                    src={manga.poster_url || 'https://placehold.co/80x120/444/CCC?text=Manga'}
                    alt={manga.title || 'Manga'}
                    className="w-full h-auto object-cover rounded-t-xl"
                    onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/80x120/444/CCC?text=Manga'; }}
                  />
                  <div className="p-3 text-center">
                    <h5 className="text-white text-sm font-semibold line-clamp-2">{manga.title}</h5>
                    <p className="text-gray-400 text-xs mt-1">{manga.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

      </div>
    </div>
  );
}

export default CharacterDetailViewer;
