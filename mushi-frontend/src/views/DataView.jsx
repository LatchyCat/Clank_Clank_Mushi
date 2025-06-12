// mushi-frontend/src/views/DataView.jsx
import React from 'react';

function DataView() {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-4xl font-bold text-purple-400 mb-4">
        Data Explorer (3D Visualization Here!)
      </h1>
      <p className="text-lg text-gray-300">
        This view will contain your Three.js visualization of clustered vector data.
      </p>
    </div>
  );
}

export default DataView;
