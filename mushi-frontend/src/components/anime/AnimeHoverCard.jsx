// src/components/anime/AnimeHoverCard.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPlus, faStar, faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { api } from '@/services/api';

const InfoLine = ({ label, value }) => {
    if (!value || (Array.isArray(value) && value.length === 0)) return null;
    return (
        <p><strong className="text-gray-200">{label}:</strong> {Array.isArray(value) ? value.join(', ') : value}</p>
    );
};

const AnimeHoverCard = ({ animeId, position, onMouseEnter, onMouseLeave }) => {
    const [details, setDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!animeId) return;

        setIsLoading(true);
        setDetails(null);

        const fetchDetails = async () => {
            try {
                // Fetch the full details now
                const data = await api.anime.getDetails(animeId);
                if (data && data.title) {
                    setDetails(data);
                } else {
                    onMouseLeave(); // Close if no data found
                }
            } catch (error) {
                console.error("Failed to fetch anime details for hover card:", error);
                onMouseLeave(); // Close on error
            } finally {
                setIsLoading(false);
            }
        };

        fetchDetails();
    }, [animeId, onMouseLeave]);

    if (!position) return null;

    const modalStyle = {
        position: 'fixed',
        top: position.top,
        left: position.left,
        zIndex: 10000,
        pointerEvents: 'auto',
        transform: 'scale(1)',
        opacity: 1,
        transition: 'opacity 0.2s ease-in-out, transform 0.2s ease-in-out',
    };

    return (
        <div style={modalStyle} onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>
            <div className="w-[380px] bg-neutral-800 rounded-xl shadow-2xl overflow-hidden flex flex-col text-white backdrop-blur-md border border-white/10">
                {isLoading ? (
                    <div className="flex items-center justify-center h-72">
                        <FontAwesomeIcon icon={faCircleNotch} className="text-pink-400 animate-spin" size="2x" />
                    </div>
                ) : details ? (
                    <>
                        <div className="p-4 bg-black/20">
                            <h2 className="text-xl font-bold line-clamp-2">{details.title}</h2>
                            {details.japanese_title && <p className="text-xs text-gray-400">{details.japanese_title}</p>}
                        </div>
                        <div className="p-4 flex flex-col flex-grow text-sm">
                            <div className="flex items-center gap-4 mb-3 text-xs">
                                {details.mal_score && <span className="flex items-center gap-1 font-bold text-yellow-400"><FontAwesomeIcon icon={faStar} /> {details.mal_score}</span>}
                                {details.show_type && <span className="px-2 py-0.5 bg-white/20 rounded-md font-semibold">{details.show_type}</span>}
                                {details.total_episodes_count > 0 && <span className="px-2 py-0.5 bg-white/20 rounded-md font-semibold">CC {details.total_episodes_count}</span>}
                            </div>
                            <p className="mb-4 text-gray-300 line-clamp-4 leading-relaxed flex-grow">{details.synopsis || "No synopsis available."}</p>
                            <div className="text-gray-400 text-xs space-y-1 mb-4 border-t border-white/10 pt-3">
                                <InfoLine label="Synonyms" value={details.synonyms} />
                                <InfoLine label="Aired" value={details.aired} />
                                <InfoLine label="Status" value={details.status} />
                                <InfoLine label="Genres" value={details.genres} />
                            </div>
                            <div className="flex items-center gap-2">
                                <Link to={`/watch/${details.id}`} className="flex-1 flex items-center justify-center gap-2 bg-yellow-400 text-black font-bold px-4 py-2 rounded-lg hover:bg-yellow-300 transition-colors transform hover:scale-105">
                                    <FontAwesomeIcon icon={faPlay} />
                                    <span>Watch now</span>
                                </Link>
                                <button className="flex items-center justify-center w-10 h-10 bg-white/20 rounded-lg hover:bg-white/30 transition-colors">
                                    <FontAwesomeIcon icon={faPlus} />
                                </button>
                            </div>
                        </div>
                    </>
                ) : null}
            </div>
        </div>
    );
};

export default AnimeHoverCard;
