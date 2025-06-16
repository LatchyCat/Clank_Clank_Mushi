import React from 'react';
import DataClusterViewer from '../components/data/DataClusterViewer';
import { BrainCircuit } from 'lucide-react';

/**
 * DataView component presents the unique 3D cluster visualization of the site's knowledge base.
 */
function DataView() {
  return (
    <div className="container mx-auto py-6">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-cyan-500 drop-shadow-lg mb-3">
          Mushi's Data Insights
        </h2>
        <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
          Welcome to the Anime Universe Explorer! This is a unique 3D visualization of all the data Mushi has learned. Each point represents a piece of information, and they are grouped together based on how similar they are.
        </p>
      </div>

      {/* The main feature component */}
      <DataClusterViewer />

      <div className="mt-12 p-6 bg-background/50 backdrop-blur-md rounded-2xl border border-border max-w-4xl mx-auto text-sm text-muted-foreground">
        <div className="flex items-start gap-4">
          <BrainCircuit className="w-10 h-10 text-teal-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-base text-foreground mb-1">How does this work?</h3>
            <p>Mushi uses a process called "embedding" to turn text into numbers. Then, a clustering algorithm (K-Means) groups these numbers. This visualization is a 3D representation of those clusters. It's a fun way to see how different anime topics relate to each other in Mushi's digital brain!</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DataView;
