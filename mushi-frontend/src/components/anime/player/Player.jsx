// mushi-frontend/src/components/anime/player/Player.jsx
import React, { useEffect, useRef } from 'react';
import Artplayer from 'artplayer';
import Hls from 'hls.js';

function Player({ option, getInstance, onVideoError }) {
  const artRef = useRef(null);

  useEffect(() => {
    // Initialize Artplayer
    const art = new Artplayer({
      ...option,
      container: artRef.current,
      // Add HLS.js support
      customType: {
        m3u8: function playM3u8(video, url, art) {
          if (Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(url);
            hls.attachMedia(video);
            art.hls = hls;
            art.once('destroy', () => hls.destroy());
          } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = url;
          } else {
            art.notice.show('Unsupported playback format: m3u8');
          }
        },
      },
    });

    // Add error handling
    art.on('error', (error, reconnect) => {
        console.error('Artplayer Error:', error);
        // MODIFIED: Check if the onVideoError prop is a function before calling it
        if (onVideoError && typeof onVideoError === 'function') {
            onVideoError(); // Notify parent component of the error
        }
        // Artplayer will attempt to reconnect automatically if reconnect is true
    });

    if (getInstance && typeof getInstance === 'function') {
      getInstance(art);
    }

    // Cleanup on component unmount
    return () => {
      if (art && art.destroy) {
        art.destroy(false);
      }
    };
  }, [option]); // MODIFIED: Re-initialize the player if options (like the URL) change

  return <div ref={artRef} className="w-full bg-black rounded-lg aspect-video"></div>;
}

export default Player;
