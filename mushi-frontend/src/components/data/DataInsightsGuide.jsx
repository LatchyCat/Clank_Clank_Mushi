// mushi-frontend/src/components/data/DataInsightsGuide.jsx
import React from 'react';
import { BrainCircuit, Mouse, ZoomIn, Info } from 'lucide-react';

const GuideSection = ({ icon, title, children }) => (
    <div className="bg-neutral-800/50 p-6 rounded-xl border border-white/10 transform transition-all hover:bg-neutral-700/50 hover:border-purple-400/50 hover:scale-[1.02]">
        <div className="flex items-center gap-3 mb-3">
            {icon}
            <h3 className="text-xl font-bold text-pink-300">{title}</h3>
        </div>
        <p className="text-gray-300 leading-relaxed">
            {children}
        </p>
    </div>
);

function DataInsightsGuide() {
    return (
        <div className="mt-12 max-w-7xl mx-auto">
            <h2 className="text-3xl font-extrabold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-cyan-500">
                How to Explore the Mushi Constellation
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <GuideSection icon={<Mouse size={24} className="text-teal-400" />} title="Controls & Interaction">
                    Use your mouse to explore! **Scroll** to smoothly zoom in and out. **Click and drag** the background to pan across the constellations. **Hover** over any node to see its title and highlight its connections. **Click and drag a node** to move it around and see the physics simulation in action!
                </GuideSection>
                <GuideSection icon={<Info size={24} className="text-teal-400" />} title="What You're Seeing">
                    You are looking at a map of Mushi's knowledge. The large, bright orbs are **Cluster Hubs**, representing a general topic. The smaller nodes are individual **documents** (anime, characters, etc.) that belong to that cluster. The closer two nodes are, the more similar Mushi thinks they are.
                </GuideSection>
                <GuideSection icon={<ZoomIn size={24} className="text-teal-400" />} title="Tips for Exploring">
                    Start by looking at the main **Cluster Topics** on the left. Find one that interests you and zoom in on its corresponding color in the map. As you zoom in, the names of individual anime and documents will appear. This is the best way to go from a high-level topic to specific data points.
                </GuideSection>
                <GuideSection icon={<BrainCircuit size={24} className="text-teal-400" />} title="How The Magic Works">
                    Mushi uses an AI process called **"embedding"** to read every document and convert its meaning into a complex list of numbers. Then, a **clustering algorithm (K-Means)** groups similar documents together. Finally, **Principal Component Analysis (PCA)** is used to intelligently project that complex data into this beautiful 2D map for you to explore.
                </GuideSection>
            </div>
        </div>
    );
}

export default DataInsightsGuide;
