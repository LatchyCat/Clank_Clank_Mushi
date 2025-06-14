// mushi-frontend/src/views/DataView.jsx
import React from 'react';
import DataClusterViewer from '../components/data/DataClusterViewer'; // Import the DataClusterViewer component

/**
 * DataView component serves as a dedicated page for displaying various data-related components.
 * Initially, it will host the DataClusterViewer.
 */
function DataView() {
  return (
    <div className="container mx-auto py-6">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Mushi's Data Insights! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>
      {/* DataClusterViewer to display the 3D clustered data */}
      <DataClusterViewer />
      {/* Later, you can add other data-related components here,
          possibly with conditional rendering for admin-only features. */}
    </div>
  );
}

export default DataView;
