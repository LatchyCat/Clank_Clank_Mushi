import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';

function VoiceActorDetailViewer({ actorId }) {
  const [actorDetails, setActorDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setIsLoading(true);
    api.anime.getVoiceActorDetails(actorId)
      .then(data => {
        if (data) {
          setActorDetails(data);
        } else {
          setError("No details found for this voice actor.");
        }
      })
      .catch(err => setError(`Failed to fetch voice actor details: ${err.message}`))
      .finally(() => setIsLoading(false));
  }, [actorId]);

  if (isLoading) return <div className="text-center p-10">Loading voice actor details...</div>;
  if (error) return <div className="text-center p-10 text-red-400">{error}</div>;
  if (!actorDetails) return null;

  return (
    <div className="p-4 md:p-6 text-gray-100">
      <h1 className="text-3xl md:text-5xl font-extrabold text-white mb-4">{actorDetails.name}</h1>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <aside className="lg:col-span-1">
          <img src={actorDetails.poster_url} alt={actorDetails.name} className="w-full h-auto object-cover rounded-2xl shadow-xl" />
        </aside>
        <main className="lg:col-span-3 space-y-8">
          <div>
            <h3 className="text-2xl font-bold mb-2 text-gray-200">About</h3>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{actorDetails.description || 'No description available.'}</p>
          </div>
          {/* You can add more details like roles played here */}
        </main>
      </div>
    </div>
  );
}

export default VoiceActorDetailViewer;
