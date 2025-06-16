// src/components/anime/actors/VoiceActorList.jsx
import React from 'react';
import VoiceActor from './VoiceActor';

function VoiceActorList({ characters }) {
  if (!characters || characters.length === 0) {
    return null; // Don't render if there's no data
  }

  return (
    <div className="bg-white/5 p-4 rounded-xl border border-white/10">
      <h3 className="text-xl font-bold mb-4 text-pink-400">Characters & Voice Actors</h3>
      <div className="space-y-3">
        {characters.map((charInfo) =>
          // A character can have multiple voice actors (e.g., Japanese, English)
          charInfo.voice_actors.map((va) => (
            <VoiceActor
              key={`${charInfo.character_id}-${va.id}`}
              character={charInfo}
              voiceActor={va}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default VoiceActorList;
