// mushi-frontend/src/views/AdminView.jsx
import React from 'react';
import DataIngestionControls from '../components/data/DataIngestionControls'; // Import the new ingestion controls component

/**
 * AdminView component serves as a protected page for administrative tasks,
 * starting with data ingestion controls. This view is accessible only after
 * successfully entering the admin password on the landing page.
 */
function AdminView() {
  return (
    <div className="container mx-auto py-6">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Welcome to the Admin Command Center, Senpai! 👑
      </h2>
      <p className="text-lg text-gray-300 text-center mb-8">
        Here, you can manage the data that powers Clank Clank Mushi. Please be careful, desu!~
      </p>
      {/* DataIngestionControls to manage data embedding */}
      <DataIngestionControls />
      {/* You can add more admin-specific components here later */}
    </div>
  );
}

export default AdminView;
