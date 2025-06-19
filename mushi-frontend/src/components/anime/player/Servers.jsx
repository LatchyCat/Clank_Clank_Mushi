// mushi-frontend/src/components/anime/player/Servers.jsx
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClosedCaptioning, faMicrophone } from '@fortawesome/free-solid-svg-icons';

const ServerGroup = ({ type, servers, currentServer, onServerSelect }) => {
    if (servers.length === 0) return null;

    const icon = type === 'sub'
        ? <FontAwesomeIcon icon={faClosedCaptioning} className="mr-2" />
        : <FontAwesomeIcon icon={faMicrophone} className="mr-2" />;

    return (
        <div className="flex items-center gap-3 border-b border-gray-700/50 py-3 last:border-b-0">
            <div className="flex items-center font-bold text-white w-20">
                {icon}
                <span>{type.toUpperCase()}</span>
            </div>
            <div className="flex flex-wrap gap-2">
                {servers.map((server) => (
                    <button
                        key={`${server.server_id}-${server.type}`}
                        onClick={() => onServerSelect(server)}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                            currentServer?.server_name === server.server_name && currentServer?.type === server.type
                                ? 'bg-yellow-400 text-black shadow-md'
                                : 'bg-gray-700/80 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        {server.server_name}
                    </button>
                ))}
            </div>
        </div>
    );
};

function Servers({ servers, currentServer, onServerSelect, isLoading }) {
    if (isLoading) {
        return <p className="text-gray-400 animate-pulse text-center py-4">Fetching servers...</p>;
    }

    if (!servers || servers.length === 0) {
        return <p className="text-gray-500 text-center py-4">No servers available for this episode.</p>;
    }

    const subServers = servers.filter(s => s.type === 'sub');
    const dubServers = servers.filter(s => s.type === 'dub');

    return (
        <div>
            <ServerGroup type="sub" servers={subServers} currentServer={currentServer} onServerSelect={onServerSelect} />
            <ServerGroup type="dub" servers={dubServers} currentServer={currentServer} onServerSelect={onServerSelect} />
        </div>
    );
}

export default Servers;
