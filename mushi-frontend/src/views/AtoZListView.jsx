// src/views/AtoZListView.jsx (NEW FILE)
import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { api } from '@/src/services/api';
import CategoryCard from '@/src/components/categorycard/CategoryCard'; // Reusing for grid display

const ALPHABET = ["All", "#", "0-9", ...Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i))];

function AtoZListView() {
  const { letter } = useParams();
  const location = useLocation();
  const [animeList, setAnimeList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const activeLetter = letter || 'All';

  useEffect(() => {
    window.scrollTo(0, 0);
    setIsLoading(true);
    setError(null);

    // Construct the category slug for the API call
    const categorySlug = `az-list/${activeLetter === 'All' ? '' : activeLetter}`;

    api.anime.getByCategory(categorySlug)
      .then(data => {
        // The API returns { data: [...] } for this endpoint
        setAnimeList(data?.data || []);
      })
      .catch(err => {
        console.error("Failed to fetch A-Z list:", err);
        setError(`Mushi couldn't fetch the list for '${activeLetter}'. Gomen'nasai!`);
      })
      .finally(() => setIsLoading(false));

  }, [activeLetter, location.key]); // Rerun when the letter changes

  return (
    <div className="container mx-auto py-6">
      <h2 className="text-3xl font-extrabold text-white text-center mb-6">A-Z Anime List</h2>

      {/* A-Z Navigation */}
      <nav className="flex flex-wrap justify-center gap-2 mb-8 p-4 bg-white/5 rounded-lg">
        {ALPHABET.map(char => (
          <Link
            key={char}
            to={`/az-list/${char}`}
            className={`px-3 py-1 rounded-md font-bold transition-colors ${
              activeLetter === char
                ? 'bg-pink-500 text-black'
                : 'bg-gray-700 text-gray-300 hover:bg-pink-400/50'
            }`}
          >
            {char}
          </Link>
        ))}
      </nav>

      {/* Results Display */}
      {isLoading && <div className="text-center p-10 text-indigo-300 animate-pulse">Mushi is sorting the library...</div>}
      {error && <div className="text-center p-10 text-red-400">{error}</div>}
      {!isLoading && !error && (
        <CategoryCard
          label={`Showing results for: ${activeLetter}`}
          data={animeList}
          showViewMore={false} // We are already on the full view
        />
      )}
    </div>
  );
}

export default AtoZListView;
