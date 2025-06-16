// src/components/anime/player/Episodelist.jsx
import React from 'react';

function EpisodeList({ episodes, currentEpisodeId, onEpisodeSelect }) {
  if (!episodes || episodes.length === 0) {
    return <p className="text-gray-400">No episodes available.</p>;
  }

  return (
    <div className="bg-white/5 p-4 rounded-xl border border-white/10 max-h-[80vh] overflow-y-auto">
      <h3 className="text-xl font-bold mb-4 text-pink-400">Episodes</h3>
      <div className="flex flex-col gap-2">
        {episodes.map((episode) => (
          <button
            key={episode.id}
            onClick={() => onEpisodeSelect(episode)}
            className={`w-full text-left p-3 rounded-lg text-sm transition-all duration-200 ${
              episode.id === currentEpisodeId
                ? 'bg-purple-600 text-white font-semibold shadow-lg'
                : 'bg-gray-700/50 text-gray-300 hover:bg-purple-500/50'
            }`}
          >
            Ep. {episode.episode_no}: {episode.title || 'Untitled'}
          </button>
        ))}
      </div>
    </div>
  );
}

export default EpisodeList;
