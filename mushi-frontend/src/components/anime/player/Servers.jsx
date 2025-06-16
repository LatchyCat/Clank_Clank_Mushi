// src/components/anime/player/Servers.jsx
import React from 'react';

function Servers({ servers, currentServer, onServerSelect, isLoading }) {
  if (isLoading) {
     return <p className="text-gray-400 animate-pulse">Fetching servers...</p>;
  }

  if (!servers || servers.length === 0) {
    return <p className="text-gray-400">No servers available for this episode.</p>;
  }

  return (
    <div className="my-4">
      <h4 className="text-lg font-semibold mb-2 text-gray-300">Available Servers:</h4>
      <div className="flex flex-wrap gap-2">
        {servers.map((server) => (
          <button
            key={`${server.server_id}-${server.type}`}
            onClick={() => onServerSelect(server)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors duration-200 ${
              currentServer?.server_name === server.server_name && currentServer?.type === server.type
                ? 'bg-teal-500 text-white shadow-md'
                : 'bg-gray-600/70 text-gray-300 hover:bg-teal-500/70'
            }`}
          >
            {server.server_name} ({server.type})
          </button>
        ))}
      </div>
    </div>
  );
}

export default Servers;
