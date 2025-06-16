// src/views/AnimeDetailView.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '@/src/services/api';

// Import our new and existing components
import VoiceActorList from '@/src/components/anime/actors/VoiceActorList';
import CategoryCard from '@/src/components/categorycard/CategoryCard'; // For related/recommended

function AnimeDetailView() {
  const { animeId } = useParams();
  const navigate = useNavigate();

  const [animeDetails, setAnimeDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    window.scrollTo(0, 0); // Scroll to top on new anime load
    setIsLoading(true);
    api.anime.getDetails(animeId)
      .then(data => {
        if (data) {
          setAnimeDetails(data);
        } else {
          setError("No details found for this anime.");
        }
      })
      .catch(err => setError(`Failed to fetch anime details: ${err.message}`))
      .finally(() => setIsLoading(false));
  }, [animeId]);

  const handleAskMushi = () => {
    if (!animeDetails) return;
    const preloadedQuery = `Tell me more about the anime "${animeDetails.title}". Here is a quick summary to give you context: ${animeDetails.synopsis}`;
    navigate('/mushi_ai', { state: { preloadedQuery } });
  };

  if (isLoading) return <div className="text-center p-10 text-indigo-300 animate-pulse">Mushi is loading the details...</div>;
  if (error) return <div className="text-center p-10 text-red-400">{error}</div>;
  if (!animeDetails) return null;

  const firstEpisodeId = animeDetails.episodes?.[0]?.id;

  // Helper for displaying info neatly
  const infoItems = [
    { label: 'Type', value: animeDetails.show_type },
    { label: 'Status', value: animeDetails.status },
    { label: 'Aired', value: animeDetails.aired },
    { label: 'Premiered', value: animeDetails.premiered },
    { label: 'Episodes', value: animeDetails.total_episodes_count || 'N/A' },
    { label: 'Duration', value: animeDetails.duration },
    { label: 'Rating', value: animeDetails.rating },
  ].filter(item => item.value); // Filter out items with no value

  return (
    <div className="p-4 md:p-6 text-gray-100">
      {/* Header with Title and Watch/Ask Buttons */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-5xl font-extrabold text-white mb-4 drop-shadow-lg">{animeDetails.title}</h1>
        <div className="flex flex-wrap gap-4">
          {firstEpisodeId && (
            <Link to={`/watch/${animeId}/${firstEpisodeId}`} className="flex-shrink-0">
              <button className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-500 text-white font-bold text-lg rounded-full shadow-lg hover:scale-105 transition-transform">
                Watch Now
              </button>
            </Link>
          )}
          <button
            onClick={handleAskMushi}
            className="px-6 py-3 bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-bold text-lg rounded-full shadow-lg hover:scale-105 transition-transform"
          >
            Ask Mushi about this...
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Sidebar / Info Column */}
        <aside className="lg:col-span-1 space-y-6">
          <img src={animeDetails.poster_url} alt={animeDetails.title} className="w-full h-auto object-cover rounded-2xl shadow-xl" />
          <div className="bg-white/5 p-4 rounded-xl border border-white/10">
            <h3 className="text-xl font-bold mb-3 text-pink-400">Information</h3>
            <div className="space-y-2 text-sm">
              {infoItems.map(item => (
                <p key={item.label}><strong className="font-semibold text-gray-300">{item.label}:</strong> {item.value}</p>
              ))}
               {animeDetails.genres?.length > 0 && (
                 <p><strong className="font-semibold text-gray-300">Genres:</strong> {animeDetails.genres.join(', ')}</p>
               )}
            </div>
          </div>
        </aside>

        {/* Right Content Area */}
        <main className="lg:col-span-3 space-y-8">
          <div>
            <h3 className="text-2xl font-bold mb-2 text-gray-200">Synopsis</h3>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{animeDetails.synopsis}</p>
          </div>

          <VoiceActorList characters={animeDetails.characters_voice_actors} />

          {animeDetails.related_anime?.length > 0 && (
             <CategoryCard
                label="Related Anime"
                data={animeDetails.related_anime}
                showViewMore={false} // Don't need a "view more" link here
             />
          )}

          {animeDetails.recommended_anime?.length > 0 && (
             <CategoryCard
                label="Recommended Anime"
                data={animeDetails.recommended_anime}
                showViewMore={false}
             />
          )}
        </main>
      </div>
    </div>
  );
}

export default AnimeDetailView;
