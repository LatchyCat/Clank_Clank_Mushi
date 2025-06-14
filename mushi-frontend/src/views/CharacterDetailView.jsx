// mushi-frontend/src/views/CharacterDetailView.jsx
import React from 'react';
import { useParams } from 'react-router-dom'; // To get the characterId from the URL
import CharacterDetailViewer from '../components/anime/characters/CharacterDetailViewer'; // Import the character detail viewer component

/**
 * CharacterDetailView component serves as a dedicated page to display the details of a single anime character.
 * It extracts the characterId from the URL parameters and passes it to the CharacterDetailViewer.
 */
function CharacterDetailView() {
  // Use useParams to extract the characterId from the URL (e.g., /app/anime/character/some-character-id)
  const { characterId } = useParams();

  if (!characterId) {
    return (
      <div className="text-red-400 text-center p-4">
        Eeeh~ Senpai, Mushi couldn't find a Character ID in the URL. Gomen'nasai! (T_T)
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      {/* CharacterDetailViewer will fetch and display details for the given characterId */}
      <CharacterDetailViewer characterId={characterId} />
    </div>
  );
}

export default CharacterDetailView;
