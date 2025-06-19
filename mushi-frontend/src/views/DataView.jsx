// mushi-frontend/src/views/DataView.jsx
import React from 'react';
import DataClusterViewer from '../components/data/DataClusterViewer';
import DataInsightsGuide from '../components/data/DataInsightsGuide';

function DataView() {
  return (
    <div className="container mx-auto py-6">
      <div className="text-center mb-10 px-4">
        <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-cyan-500 drop-shadow-lg mb-3">
          Mushi's Data Insights
        </h2>
        <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
          Welcome to the Anime Universe Explorer! This is a living map of all the data Mushi has learned. Drag, zoom, and hover to explore the relationships between different anime, characters, and topics.
        </p>
      </div>

      <DataClusterViewer />

      <DataInsightsGuide />
    </div>
  );
}

export default DataView;
