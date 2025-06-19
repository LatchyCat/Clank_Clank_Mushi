// mushi-frontend/src/views/WatchView.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronRight, Tv, Film, Star } from 'lucide-react';

import { api } from '@/services/api';
import Player from '@/components/anime/player/Player';
import EpisodeList from '@/components/anime/player/Episodelist';
import Servers from '@/components/anime/player/Servers';

const AnimeDetailsSidebar = ({ anime }) => {
    if (!anime) return null;
    const getIcon = (type) => {
        if (type?.toLowerCase() === 'tv') return <Tv className="w-4 h-4" />;
        if (type?.toLowerCase() === 'movie') return <Film className="w-4 h-4" />;
        return <Tv className="w-4 h-4" />;
    };
    return (
        <div className="bg-[#1a1a1a] p-4 rounded-lg space-y-4">
            <img src={anime.poster_url} alt={anime.title} className="w-full h-auto object-cover rounded-md" />
            <div>
                <Link to={`/anime/details/${anime.id}`} className="text-lg font-bold text-white hover:text-pink-400 line-clamp-2">{anime.title}</Link>
                <div className="flex flex-wrap items-center gap-2 mt-2 text-xs text-gray-300">
                    <span className="bg-white/10 px-2 py-1 rounded-md">PG-13</span>
                    <span className="bg-yellow-500/80 text-black font-bold px-2 py-1 rounded-md">HD</span>
                    <span className="flex items-center gap-1"><Star className="w-4 h-4 text-yellow-400" /> {anime.mal_score || 'N/A'}</span>
                </div>
                <p className="text-sm text-gray-400 mt-3 line-clamp-4 leading-relaxed">{anime.synopsis}</p>
                <Link to={`/anime/details/${anime.id}`} className="text-pink-400 text-sm font-semibold hover:underline mt-1 block">View detail</Link>
            </div>
        </div>
    );
};

function WatchView() {
    const { animeId, episodeId } = useParams();
    const navigate = useNavigate();

    const [animeDetails, setAnimeDetails] = useState(null);
    const [currentEpisode, setCurrentEpisode] = useState(null);
    const [servers, setServers] = useState([]);
    const [currentServer, setCurrentServer] = useState(null);
    const [streamUrl, setStreamUrl] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [playerStatus, setPlayerStatus] = useState("Loading Anime Info...");
    const [error, setError] = useState(null);

    // Effect 1: Fetch initial anime details, including the episode list
    useEffect(() => {
        setIsLoading(true);
        setPlayerStatus("Loading Anime Info...");
        api.anime.getDetails(animeId)
          .then(data => {
            if (!data || !data.episodes) throw new Error("Anime details or episode list missing.");
            setAnimeDetails(data);

            let targetEpisode = episodeId
                ? data.episodes.find(ep => ep.id === episodeId)
                : data.episodes[0];

            if (targetEpisode) {
                if (!episodeId) {
                    navigate(`/watch/${animeId}/${targetEpisode.id}`, { replace: true });
                }
                setCurrentEpisode(targetEpisode);
            } else {
                setPlayerStatus("Episode not found. Redirecting to the first episode.");
                navigate(`/watch/${animeId}/${data.episodes[0].id}`, { replace: true });
            }
          })
          .catch(err => {
            setError(`Failed to load anime details: ${err.message}`);
            setPlayerStatus(`Error: ${err.message}`);
          })
          .finally(() => setIsLoading(false));
    }, [animeId, episodeId, navigate]);

    // Effect 2: Fetch servers once we have a currentEpisode
    useEffect(() => {
        if (!currentEpisode?.data_id) return;

        setPlayerStatus(`Fetching servers for Ep. ${currentEpisode.episode_no}...`);
        api.anime.getAvailableServers(currentEpisode.data_id)
            .then(data => {
                if (data?.servers?.length > 0) {
                    setServers(data.servers);
                    // Automatically select the first 'sub' server, or the very first server as a fallback
                    const subServer = data.servers.find(s => s.type === 'sub' && s.server_name === 'Vidcloud') || data.servers[0];
                    setCurrentServer(subServer);
                } else {
                    setPlayerStatus("No streaming servers were found for this episode.");
                    setServers([]);
                }
            })
            .catch(err => {
                setPlayerStatus(`Error fetching servers: ${err.message}`);
            });
    }, [currentEpisode]);

    // --- START OF FIX: Corrected API call and dependencies ---
    // Effect 3: Fetch the stream URL once we have a current server selected
    useEffect(() => {
        // Guard against running without all necessary data
        if (!animeId || !currentServer || !currentEpisode?.id) return;

        setPlayerStatus(`Loading stream from ${currentServer.server_name}...`);
        setStreamUrl(''); // Clear previous stream URL
        setError(null);   // Clear previous errors

        // Call the API with the correct arguments in the correct order.
        api.anime.getStreamingInfo(animeId, currentEpisode.data_id, currentServer.server_name, currentServer.type)
          .then(data => {
            if (data?.streaming_links?.[0]?.file) {
              setStreamUrl(data.streaming_links[0].file);
              setPlayerStatus(null); // Clear status on success
            } else {
              const errorMessage = data?.error || "Failed to get a streaming link. Please try another server.";
              setPlayerStatus(errorMessage);
              setError(errorMessage);
            }
          }).catch((err) => {
              const errorMessage = err.message || "Could not load stream. The proxy server might be offline or the source is invalid.";
              setPlayerStatus(errorMessage);
              setError(errorMessage);
          });
    }, [animeId, currentServer, currentEpisode]); // Updated dependency array
    // --- END OF FIX ---


    const handleEpisodeSelect = (episode) => navigate(`/watch/${animeId}/${episode.id}`);
    const handleVideoError = () => setPlayerStatus("Video playback error. The stream source may be invalid or the proxy isn't working.");

    if (isLoading) {
        return <div className="text-center p-10 text-indigo-300 animate-pulse">Mushi is charting a course to the watch room...</div>;
    }

    const playerOption = {
        url: streamUrl,
        title: `${animeDetails?.title} - Ep ${currentEpisode?.episode_no || ''}`,
        poster: animeDetails?.poster_url
    };

    return (
        <div className="container mx-auto">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-4">
                <Link to="/home" className="hover:text-white">Home</Link>
                <ChevronRight size={16} />
                <span className="text-white truncate">{animeDetails?.title || "Loading..."}</span>
            </div>

            <div className="grid grid-cols-12 gap-6">
                <div className="lg:col-span-3 col-span-12">
                    <EpisodeList
                        episodes={animeDetails?.episodes || []}
                        currentEpisodeId={currentEpisode?.id}
                        onEpisodeSelect={handleEpisodeSelect}
                    />
                </div>

                <div className="lg:col-span-6 col-span-12">
                    <div className="w-full bg-black rounded-lg aspect-video flex items-center justify-center text-white">
                        {streamUrl ? (
                            <Player option={playerOption} onVideoError={handleVideoError} />
                        ) : (
                            <p className="text-gray-300 animate-pulse p-4 text-center">{playerStatus}</p>
                        )}
                    </div>
                    <div className="mt-4 p-4 bg-[#1a1a1a] rounded-lg">
                        <div className="bg-yellow-100/20 text-yellow-200 text-sm p-3 rounded-md mb-4">
                             You are watching <strong>Episode {currentEpisode?.episode_no || 'N/A'}</strong>. If current server doesn't work, please try other servers besides.
                        </div>
                        <Servers
                            servers={servers}
                            currentServer={currentServer}
                            onServerSelect={setCurrentServer}
                            isLoading={isLoading}
                        />
                    </div>
                </div>

                <div className="lg:col-span-3 col-span-12">
                    <AnimeDetailsSidebar anime={animeDetails} />
                </div>
            </div>
        </div>
    );
}

export default WatchView;
