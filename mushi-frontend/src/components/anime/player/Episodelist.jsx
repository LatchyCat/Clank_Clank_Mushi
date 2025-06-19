// mushi-frontend/src/components/anime/player/Episodelist.jsx
import React, { useState } from 'react';
import { Search, Play } from 'lucide-react';

function EpisodeList({ episodes, currentEpisodeId, onEpisodeSelect }) {
    const [searchTerm, setSearchTerm] = useState('');

    const filteredEpisodes = episodes.filter(ep =>
        ep.episode_no?.toString().includes(searchTerm) ||
        ep.title?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="bg-[#1a1a1a] p-4 rounded-lg h-full flex flex-col">
            <h3 className="text-lg font-bold text-white mb-3">List of episodes:</h3>
            <div className="relative mb-4">
                <input
                    type="text"
                    placeholder="Number of Ep"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full bg-[#2a2a2a] border border-gray-600 rounded-md py-2 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-pink-500"
                />
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>

            <div className="flex-grow overflow-y-auto custom-scrollbar pr-2">
                {filteredEpisodes.length > 0 ? (
                    <div className="flex flex-col gap-2">
                        {filteredEpisodes.map((episode) => (
                            <button
                                key={episode.id}
                                onClick={() => onEpisodeSelect(episode)}
                                className={`w-full text-left p-3 rounded-lg text-sm transition-all duration-200 flex items-center justify-between ${
                                    episode.id === currentEpisodeId
                                        ? 'bg-pink-600 text-white font-semibold shadow-lg'
                                        : 'bg-[#2a2a2a] text-gray-300 hover:bg-white/10'
                                }`}
                            >
                                <span className="flex items-center gap-3">
                                    <span className="font-bold w-6 text-center">{episode.episode_no}</span>
                                    <span className="line-clamp-1">{episode.title || 'Untitled'}</span>
                                </span>
                                {episode.id === currentEpisodeId && <Play className="w-5 h-5" />}
                            </button>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-500 text-center py-10">No episodes found.</p>
                )}
            </div>
        </div>
    );
}

export default EpisodeList;
