// mushi-frontend/src/components/one-piece/OnePieceDevilFruitsList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // Correct path to api.js

/**
 * OnePieceDevilFruitsList component fetches and displays a list of One Piece Devil Fruits.
 */
function OnePieceDevilFruitsList() {
  const [devilFruits, setDevilFruits] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDevilFruits = async () => {
      try {
        setIsLoading(true);
        setError(null); // Clear any previous errors
        const data = await api.onePiece.getFruits(); // Fetch One Piece Devil Fruits

        if (data) {
          setDevilFruits(data);
          console.log("Mushi found all the mysterious Devil Fruits for you, Senpai! Waku waku!~ ☆", data);
        } else {
          setError("Muu... Mushi couldn't fetch the One Piece Devil Fruits. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch One Piece Devil Fruits:", err);
        setError(`Mushi encountered an error while fetching One Piece Devil Fruits: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDevilFruits();
  }, []); // Empty dependency array means this effect runs once on mount

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is searching for all the yummy (but dangerous!) Devil Fruits for you, Senpai! Kira kira!~ ✨
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

  if (!devilFruits || devilFruits.length === 0) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No One Piece Devil Fruits found. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        One Piece Devil Fruits! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {devilFruits.map((fruit) => (
          <div key={fruit.id} className="bg-gray-800 rounded-lg shadow-lg p-3 text-center transform hover:scale-105 transition-transform duration-300">
            {/* Assuming fruit object has 'name' and 'type' */}
            <h3 className="text-white text-md font-semibold truncate mb-1">{fruit.name}</h3>
            {fruit.type && <p className="text-gray-400 text-sm">{fruit.type}</p>}
            {/* You could add more details here or link to a detail page if one existed */}
          </div>
        ))}
      </div>
    </div>
  );
}

export default OnePieceDevilFruitsList;
