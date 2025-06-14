// mushi-frontend/src/views/HomeView.jsx
import React from 'react';
import AnimeHomeDashboard from '../components/anime/AnimeHomeDashboard'; // Import the new component

/**
 * HomeView component displays the main dashboard with various anime lists.
 * Its job is to arrange components that assist the user in exploring anime data.
 */
function HomeView() {
  return (
    <div className="container mx-auto py-6">
      {/* The HomeView primarily acts as a container for the AnimeHomeDashboard */}
      <AnimeHomeDashboard />
    </div>
  );
}

export default HomeView;
