// mushi-frontend/src/components/navigation/TopNavMegaMenu.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAppData } from '@/context/AppDataContext';

// --- COMPLETELY REBUILT CARD COMPONENT ---
// This new structure ensures the text is an overlay on the image, preventing any empty space below.
const MegaMenuAnimeCard = ({ anime }) => {
    if (!anime) return null;
    return (
        <Link to={`/anime/details/${anime.id}`} className="group block rounded-lg overflow-hidden relative shadow-lg">
            {/* Image Container */}
            <div className="h-48 w-full">
                <img
                    src={anime.poster_url || anime.poster}
                    alt={anime.title}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                />
            </div>
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
            {/* Text Content Overlay */}
            <div className="absolute bottom-0 left-0 p-2 w-full">
                <h4 className="font-semibold text-white text-sm line-clamp-2 transition-colors group-hover:text-pink-300">{anime.title}</h4>
                <p className="text-xs text-gray-400">{anime.show_type || anime.tvInfo?.showType}</p>
            </div>
        </Link>
    );
};


const MegaMenuColumn = ({ title, items, isGenre = false }) => (
    <div className="flex flex-col gap-2 h-full">
        <h3 className="font-bold text-sm text-pink-300 uppercase tracking-wider mb-2 flex-shrink-0">{title}</h3>
        <div className="flex flex-col gap-1 overflow-hidden">
            {items.map(item => {
                const linkTarget = isGenre
                    ? `/search?category=genre/${item.slug.toLowerCase()}&title=${encodeURIComponent(item.name)}`
                    : `/anime/details/${item.id}`;

                return (
                    <Link
                        key={item.slug || item.id}
                        to={linkTarget}
                        className="text-gray-300 hover:text-white hover:bg-white/10 p-2 rounded-md transition-colors text-base whitespace-nowrap truncate"
                    >
                        {item.name || item.title}
                    </Link>
                );
            })}
        </div>
    </div>
);

function TopNavMegaMenu() {
    const { menuData, isLoading } = useAppData();

    if (isLoading || !menuData) {
        return <div className="p-6 text-center text-gray-400" style={{ width: '1024px', height: '320px' }}>Mushi is loading the menu...</div>
    }

    return (
        <div className="p-6 w-full max-w-6xl" style={{ width: '1024px' }}>
            <div className="grid grid-cols-12 gap-x-6">
                <div className="col-span-6 grid grid-cols-3 gap-x-6">
                    <MegaMenuColumn title="Trending Now" items={menuData.trending} />
                    <MegaMenuColumn title="Top Airing" items={menuData.topAiring} />
                    <MegaMenuColumn title="Popular Genres" items={menuData.genres} isGenre={true} />
                </div>

                <div className="col-span-1 flex justify-center">
                    <div className="w-px bg-white/10 h-full"></div>
                </div>

                {/* --- No changes needed here, the fix is in the Card component itself --- */}
                <div className="col-span-5 flex flex-col">
                    <h3 className="font-bold text-sm text-pink-300 uppercase tracking-wider mb-2 flex-shrink-0">Most Popular This Week</h3>
                    <div className="grid grid-cols-3 gap-4 flex-grow">
                        {menuData.mostPopular.map(anime => (
                            <MegaMenuAnimeCard key={anime.id} anime={anime} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default TopNavMegaMenu;
