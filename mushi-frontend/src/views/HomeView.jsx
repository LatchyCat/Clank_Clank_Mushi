// mushi-frontend/src/views/HomeView.jsx
import React, { useState, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAppData } from '@/context/AppDataContext';

import Spotlight from '@/components/spotlight/Spotlight';
import Trending from '@/components/trending/Trending';
import CategoryCard from '@/components/categorycard/CategoryCard';
import Cart from '@/components/cart/Cart';
import AnimeHoverCard from '@/components/anime/AnimeHoverCard';

function HomeView() {
  const { homeData, isLoading, error } = useAppData();

  const [hoveredInfo, setHoveredInfo] = useState({ animeId: null, position: null });
  const hoverTimeoutRef = useRef(null);
  const cardRefs = useRef({});

  const handleCardMouseEnter = useCallback((animeId, element) => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);

    hoverTimeoutRef.current = setTimeout(() => {
        if (!element) return;

        const rect = element.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const modalWidth = 380;
        const space = 15;

        let left = (rect.right + modalWidth + space < viewportWidth)
          ? rect.left + rect.width + space
          : rect.left - modalWidth - space;

        setHoveredInfo({
            animeId: animeId,
            position: { top: rect.top, left }
        });

    }, 400);

  }, []);

  const handleMouseLeave = useCallback(() => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);

    hoverTimeoutRef.current = setTimeout(() => {
      setHoveredInfo({ animeId: null, position: null });
    }, 300);
  }, []);

  const handleHoverCardEnter = useCallback(() => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen-75 text-indigo-300 text-lg">
        Mushi is preparing your awesome anime dashboard! Please wait warmly~ (≧∇≦)/
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-6 border border-red-500 rounded-lg bg-red-900/30 text-lg mx-auto max-w-lg shadow-lg">
        Oh no! Mushi couldn't load the initial app data: {error}
      </div>
    );
  }

  if (!homeData) {
    return <div className="text-gray-400 text-center p-6 text-lg">Muu... No anime home data was found.</div>;
  }

  return (
    <div className="w-full space-y-12">
       {hoveredInfo.animeId && (
        <AnimeHoverCard
            animeId={hoveredInfo.animeId}
            position={hoveredInfo.position}
            onMouseEnter={handleHoverCardEnter}
            onMouseLeave={handleMouseLeave}
        />
      )}

      {homeData.spotlights && homeData.spotlights.length > 0 && <Spotlight spotlights={homeData.spotlights} />}

      {homeData.trending && homeData.trending.length > 0 && (
        <div className="p-4 md:p-0">
          <h2 className="font-bold text-2xl text-[#ffbade] capitalize mb-4">Trending</h2>
          <Trending trending={homeData.trending} />
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-8 mt-8 px-4 md:px-0">
        <main className="flex-grow lg:w-3/4 space-y-12">
          {homeData.latest_episode && homeData.latest_episode.length > 0 && (
            <CategoryCard
              label="Latest Episodes"
              data={homeData.latest_episode}
              path="recently-updated"
              cardRefs={cardRefs}
              onMouseEnter={handleCardMouseEnter}
              onMouseLeave={handleMouseLeave}
            />
          )}
          {homeData.latest_completed && homeData.latest_completed.length > 0 && (
            <CategoryCard
              label="Recently Completed"
              data={homeData.latest_completed}
              path="completed"
              cardRefs={cardRefs}
              onMouseEnter={handleCardMouseEnter}
              onMouseLeave={handleMouseLeave}
            />
          )}
        </main>
        <aside className="lg:w-1/4 flex-shrink-0 space-y-12">
          {/* --- START OF FIX: Added titles for sidebar sections --- */}
          {homeData.top_airing && homeData.top_airing.length > 0 && (
            <div>
              <h2 className="font-bold text-2xl text-[#ffbade] capitalize mb-4">Top Airing</h2>
              <Cart
                data={homeData.top_airing}
                cardRefs={cardRefs}
                onMouseEnter={handleCardMouseEnter}
                onMouseLeave={handleMouseLeave}
              />
            </div>
          )}
          {homeData.most_popular && homeData.most_popular.length > 0 && (
            <div>
              <h2 className="font-bold text-2xl text-[#ffbade] capitalize mb-4">Most Popular</h2>
              <Cart
                data={homeData.most_popular}
                cardRefs={cardRefs}
                onMouseEnter={handleCardMouseEnter}
                onMouseLeave={handleMouseLeave}
              />
            </div>
          )}
           {homeData.most_favorite && homeData.most_favorite.length > 0 && (
            <div>
               <h2 className="font-bold text-2xl text-[#ffbade] capitalize mb-4">Most Favorited</h2>
               <Cart
                data={homeData.most_favorite}
                cardRefs={cardRefs}
                onMouseEnter={handleCardMouseEnter}
                onMouseLeave={handleMouseLeave}
              />
            </div>
          )}
          {/* --- END OF FIX --- */}
        </aside>
      </div>
    </div>
  );
}

export default HomeView;
