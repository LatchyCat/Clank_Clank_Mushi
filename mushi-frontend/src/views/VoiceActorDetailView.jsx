// mushi-frontend/src/views/VoiceActorDetailView.jsx
import React from 'react';
import { useParams } from 'react-router-dom'; // To get the actorId from the URL
import VoiceActorDetailViewer from '../components/anime/actors/VoiceActorDetailViewer'; // Import the voice actor detail viewer component

/**
 * VoiceActorDetailView component serves as a dedicated page to display the details of a single voice actor.
 * It extracts the actorId from the URL parameters and passes it to the VoiceActorDetailViewer.
 */
function VoiceActorDetailView() {
  // Use useParams to extract the actorId from the URL (e.g., /app/anime/actors/some-actor-id)
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
      {/* VoiceActorDetailViewer will fetch and display details for the given actorId */}
      <VoiceActorDetailViewer actorId={actorId} />
    </div>
  );
}

export default VoiceActorDetailView;
