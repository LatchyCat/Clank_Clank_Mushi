// mushi-frontend/src/components/one-piece/OnePieceCharacterList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Correct path to api.js

/**
 * OnePieceCharacterList component fetches and displays a list of One Piece characters.
 */
function OnePieceCharacterList() {
  const [characters, setCharacters] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        setIsLoading(true);
        setError(null); // Clear any previous errors
        const data = await api.onePiece.getCharacters(); // Fetch One Piece characters

        if (data) {
          setCharacters(data);
          console.log("Mushi found all the amazing One Piece characters for you, Senpai! Waku waku!~ ☆", data);
        } else {
          setError("Muu... Mushi couldn't fetch the One Piece characters. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch One Piece characters:", err);
        setError(`Mushi encountered an error while fetching One Piece characters: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCharacters();
  }, []); // Empty dependency array means this effect runs once on mount

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is looking for all the nakama for you, Senpai! Kira kira!~ ✨
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

  if (!characters || characters.length === 0) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No One Piece characters found. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        One Piece Characters! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {characters.map((character) => (
          <div key={character.id} className="bg-gray-800 rounded-lg shadow-lg p-3 text-center transform hover:scale-105 transition-transform duration-300">
            {/* Assuming character object has 'name' and 'image' or 'poster_url' */}
            <img
              src={character.image || character.poster_url || 'https://placehold.co/100x100/333/FFF?text=Char'}
              alt={character.name || 'Character Image'}
              className="w-24 h-24 rounded-full object-cover mx-auto mb-2 border-2 border-indigo-500"
              onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/100x100/333/FFF?text=Char'; }}
            />
            <h3 className="text-white text-md font-semibold truncate">{character.name}</h3>
            {character.role && <p className="text-gray-400 text-sm">{character.role}</p>}
            {/* You can add a link to a character detail page here if one exists/will be created */}
            {/* <Link to={`/app/onepiece/character/${character.id}`} className="text-indigo-400 hover:text-indigo-300 text-xs mt-1">Details~</Link> */}
          </div>
        ))}
      </div>
    </div>
  );
}

export default OnePieceCharacterList;
