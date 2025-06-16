// mushi-frontend/src/views/HomeView.jsx
import React, { useState, useEffect } from 'react';

// CORRECTED IMPORTS
import { api } from '@/services/api';
import Spotlight from '@/components/spotlight/Spotlight';
import Trending from '@/components/trending/Trending';
import CategoryCard from '@/components/categorycard/CategoryCard';
import Cart from '@/components/cart/Cart';

function HomeView() {
  const [homeData, setHomeData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHomeData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.anime.getHomeData();
        if (data) {
          setHomeData(data);
          console.log("Mushi fetched home data, Senpai! ✨", data);
        } else {
          setError("Mushi couldn't fetch the home data, gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch home data:", err);
        setError(`Mushi encountered an error while fetching home data: ${err.message}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHomeData();
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
        Oh no! {error}
      </div>
    );
  }

  if (!homeData) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg">
        Muu... No anime home data was found. Please check the backend. (T_T)
      </div>
    );
  }

  return (
    <div className="w-full space-y-12">
      {homeData.spotlights && <Spotlight spotlights={homeData.spotlights} />}
      {homeData.trending && <Trending trending={homeData.trending} />}
      <div className="flex flex-col lg:flex-row gap-8 mt-8">
        <main className="flex-grow lg:w-3/4 space-y-12">
          {homeData.latest_episode && (
            <CategoryCard
              label="Latest Episodes"
              data={homeData.latest_episode}
              path="latest-episodes"
            />
          )}
          {homeData.latest_completed && (
            <CategoryCard
              label="Recently Completed"
              data={homeData.latest_completed}
              path="completed"
            />
          )}
        </main>
        <aside className="lg:w-1/4 flex-shrink-0 space-y-12">
          {homeData.top_airing && (
            <Cart
              label="Top Airing"
              data={homeData.top_airing}
              path="top-airing"
            />
          )}
          {homeData.most_popular && (
            <Cart
              label="Most Popular"
              data={homeData.most_popular}
              path="most-popular"
            />
          )}
           {homeData.most_favorite && (
            <Cart
              label="Most Favorited"
              data={homeData.most_favorite}
              path="most-favorite"
            />
          )}
        </aside>
      </div>
    </div>
  );
}

export default HomeView;
