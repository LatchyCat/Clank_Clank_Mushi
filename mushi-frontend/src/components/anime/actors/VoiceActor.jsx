// src/components/anime/actors/VoiceActor.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function VoiceActor({ character, voiceActor }) {
  return (
    <div className="flex items-center gap-3 p-2 bg-gray-800/50 rounded-lg transition-colors hover:bg-gray-700/70">
      {/* Character Info */}
      <Link to={`/anime/character/${character.character_id}`} className="flex items-center gap-2 flex-1 hover:opacity-80 transition-opacity">
        <img
          src={character.character_poster_url}
          alt={character.character_name}
          className="w-12 h-12 object-cover rounded-md flex-shrink-0"
        />
        <div className="text-left">
          <p className="text-sm font-semibold text-gray-200 line-clamp-2">{character.character_name}</p>
          <p className="text-xs text-gray-400">{character.character_cast}</p>
        </div>
      </Link>

      {/* Voice Actor Info */}
      <Link to={`/anime/actors/${voiceActor.id}`} className="flex items-center gap-2 flex-1 text-right justify-end hover:opacity-80 transition-opacity">
        <div className="text-right">
          <p className="text-sm font-semibold text-gray-200 line-clamp-2">{voiceActor.name}</p>
          <p className="text-xs text-gray-400">Voice Actor</p>
        </div>
        <img
          src={voiceActor.poster_url}
          alt={voiceActor.name}
          className="w-12 h-12 object-cover rounded-md flex-shrink-0"
        />
      </Link>
    </div>
  );
}

export default VoiceActor;
