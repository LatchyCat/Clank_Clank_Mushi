import React from 'react';
import DataIngestionControls from '../components/data/DataIngestionControls';
import { AlertTriangle } from 'lucide-react';

/**
 * AdminView serves as the command center for managing the site's data knowledge base.
 */
function AdminView() {
  return (
    <div className="container mx-auto py-6">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500 drop-shadow-lg mb-3">
          Admin Command Center
        </h2>
        <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
          This is the control panel for Mushi's knowledge base. Use these tools to ingest new data and update the vector store.
        </p>
      </div>

      <div className="max-w-3xl mx-auto p-6 bg-destructive/10 border border-destructive/30 rounded-lg mb-8 text-destructive-foreground">
        <div className="flex items-center gap-4">
          <AlertTriangle className="w-8 h-8 flex-shrink-0" />
          <p className="text-sm">
            <span className="font-bold">Warning:</span> These actions directly modify the site's data. Ingesting large amounts of data can be resource-intensive and take a long time. Proceed with caution.
          </p>
        </div>
      </div>

      {/* The main admin controls component */}
      <DataIngestionControls />

    </div>
  );
}

export default AdminView;
