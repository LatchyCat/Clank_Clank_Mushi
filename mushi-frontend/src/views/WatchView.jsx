// src/views/WatchView.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';

// CORRECTED IMPORTS
import { api } from '@/services/api';
import Player from '@/components/anime/player/Player';
import EpisodeList from '@/components/anime/player/Episodelist';
import Servers from '@/components/anime/player/Servers';

function WatchView() {
  const { animeId, episodeId } = useParams();
  const navigate = useNavigate();

  const [animeDetails, setAnimeDetails] = useState(null);
  const [currentEpisode, setCurrentEpisode] = useState(null);
  const [servers, setServers] = useState([]);
  const [currentServer, setCurrentServer] = useState(null);
  const [streamUrl, setStreamUrl] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playerStatus, setPlayerStatus] = useState("Loading...");

  useEffect(() => {
    setIsLoading(true);
    api.anime.getDetails(animeId)
      .then(data => {
        setAnimeDetails(data);
        const targetEpisode = data.episodes.find(ep => ep.id === episodeId);
        if (targetEpisode) {
          setCurrentEpisode(targetEpisode);
        } else if (data.episodes.length > 0) {
          navigate(`/watch/${animeId}/${data.episodes[0].id}`, { replace: true });
        } else {
          setError("This anime has no episodes available.");
        }
      })
      .catch(err => setError(`Failed to load anime details: ${err.message}`))
      .finally(() => setIsLoading(false));
  }, [animeId, episodeId, navigate]);

  useEffect(() => {
    if (!currentEpisode) return;
    setPlayerStatus("Fetching server list...");
    setServers([]);
    setCurrentServer(null);
    setStreamUrl('');

    api.anime.getAvailableServers(animeId, currentEpisode.data_id)
      .then(data => {
        if (data?.servers?.length > 0) {
          setServers(data.servers);
          setCurrentServer(data.servers[0]);
        } else {
          setPlayerStatus("No servers found for this episode.");
        }
      })
      .catch(err => setPlayerStatus(`Error fetching servers: ${err.message}`));
  }, [currentEpisode, animeId]);

  useEffect(() => {
    if (!currentServer || !currentEpisode) return;
    setPlayerStatus(`Loading stream from ${currentServer.server_name}...`);

    api.anime.getStreamingInfo(currentEpisode.id, currentServer.server_name, currentServer.type)
      .then(data => {
        if (data?.streaming_links?.[0]?.file) {
          const info = data.streaming_links[0];
          const referer = info.headers?.Referer || info.headers?.referer;
          let src = `http://127.0.0.1:8001/api/anime/proxy-stream?url=${encodeURIComponent(info.file)}`;
          if (referer) {
            src += `&referer=${encodeURIComponent(referer)}`;
          }
          setStreamUrl(src);
          setPlayerStatus(null);
        } else {
          setPlayerStatus("Failed to get streaming link from this server.");
        }
      })
      .catch(err => setPlayerStatus(`Error getting stream: ${err.message}`));
  }, [currentServer, currentEpisode]);

  const handleEpisodeSelect = (episode) => {
    navigate(`/watch/${animeId}/${episode.id}`);
  };

  if (isLoading) return <div className="text-center p-10">Loading anime...</div>;
  if (error) return <div className="text-center p-10 text-red-400">{error}</div>;
  if (!animeDetails) return null;

  const playerOption = {
    url: streamUrl,
    title: `${animeDetails.title} - Ep ${currentEpisode?.episode_no}`,
    poster: animeDetails.poster_url,
    volume: 0.5,
    isLive: false,
    autoplay: true,
    autoSize: true,
    fullscreen: true,
    backdrop: true,
  };

  return (
    <div className="flex flex-col lg:flex-row gap-8">
      <main className="lg:w-3/4">
        <h2 className="text-2xl md:text-3xl font-bold mb-2 text-white">
          <Link to={`/anime/details/${animeId}`} className="hover:text-pink-400">
            {animeDetails.title}
          </Link>
        </h2>
        <p className="text-lg text-gray-300 mb-4">
          Episode {currentEpisode?.episode_no}: {currentEpisode?.title}
        </p>

        {playerStatus ? (
          <div className="w-full bg-black rounded-lg aspect-video flex items-center justify-center">
            <p className="text-gray-300 animate-pulse">{playerStatus}</p>
          </div>
        ) : (
          <Player option={playerOption} />
        )}

        <Servers
          servers={servers}
          currentServer={currentServer}
          onServerSelect={setCurrentServer}
        />

        <div className="mt-6 p-4 bg-white/5 rounded-xl">
          <h3 className="text-xl font-bold text-gray-200">Synopsis</h3>
          <p className="text-gray-400 mt-2 text-sm">{animeDetails.synopsis}</p>
        </div>
      </main>

      <aside className="lg:w-1/4 flex-shrink-0">
        <EpisodeList
          episodes={animeDetails.episodes}
          currentEpisodeId={currentEpisode?.id}
          onEpisodeSelect={handleEpisodeSelect}
        />
      </aside>
    </div>
  );
}

export default WatchView;
