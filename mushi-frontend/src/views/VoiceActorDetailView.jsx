// mushi-frontend/src/views/VoiceActorDetailView.jsx
import React from 'react';
import { useParams } from 'react-router-dom';
import VoiceActorDetailViewer from '@/components/anime/actors/VoiceActorDetailViewer';

function VoiceActorDetailView() {
  const { actorId } = useParams();

  if (!actorId) {
    return (
      <div className="text-red-400 text-center p-4">
        Eeeh~ Senpai, Mushi couldn't find an Actor ID in the URL. Gomen'nasai! (T_T)
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <VoiceActorDetailViewer actorId={actorId} />
    </div>
  );
}

export default VoiceActorDetailView;
