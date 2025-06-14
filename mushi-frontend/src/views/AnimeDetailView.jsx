// mushi-frontend/src/views/AnimeDetailView.jsx
import React from 'react';
import { useParams } from 'react-router-dom'; // To get the animeId from the URL
import AnimeDetailViewer from '../components/anime/details/AnimeDetailViewer'; // Import the detail viewer component

/**
 * AnimeDetailView component serves as a dedicated page to display the details of a single anime.
 * It extracts the animeId from the URL parameters and passes it to the AnimeDetailViewer.
 */
function AnimeDetailView() {
  // Use useParams to extract the animeId from the URL (e.g., /app/anime/details/some-anime-id)
  const { animeId } = useParams();

  if (!animeId) {
    return (
      <div className="text-red-400 text-center p-4">
        Eeeh~ Senpai, Mushi couldn't find an Anime ID in the URL. Gomen'nasai! (T_T)
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      {/* AnimeDetailViewer will fetch and display details for the given animeId */}
      <AnimeDetailViewer animeId={animeId} />
    </div>
  );
}

export default AnimeDetailView;
