// mushi-frontend/src/views/HomeView.jsx
import React, { useState, useEffect } from 'react';

// Import the API service to fetch data
import { api } from '@/src/services/api';

// Import the new dashboard components
import Spotlight from '@/src/components/spotlight/Spotlight';
import Trending from '@/src/components/trending/Trending';
import CategoryCard from '@/src/components/categorycard/CategoryCard';
import Cart from '@/src/components/cart/Cart';

/**
 * HomeView component now functions as a rich dashboard.
 * It fetches all necessary data from the /api/anime/home endpoint
 * and distributes it to specialized child components.
 */
function HomeView() {
  const [homeData, setHomeData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Define an async function to fetch data when the component mounts
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
  }, []); // Empty dependency array ensures this runs only once on mount

  // --- Render Loading State ---
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen-75 text-indigo-300 text-lg">
        Mushi is preparing your awesome anime dashboard! Please wait warmly~ (≧∇≦)/
      </div>
    );
  }

  // --- Render Error State ---
  if (error) {
    return (
      <div className="text-red-400 text-center p-6 border border-red-500 rounded-lg bg-red-900/30 text-lg mx-auto max-w-lg shadow-lg">
        Oh no! {error}
      </div>
    );
  }

  // --- Render "No Data" State ---
  if (!homeData) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg">
        Muu... No anime home data was found. Please check the backend. (T_T)
      </div>
    );
  }

  // --- Render Success State: The Dashboard ---
  return (
    // We remove the old background and container, as the App's layout handles it.
    // This view is now focused on arranging its components.
    <div className="w-full space-y-12">
      {/* Spotlight/Hero section at the top */}
      {homeData.spotlights && <Spotlight spotlights={homeData.spotlights} />}

      {/* Trending slider below the spotlight */}
      {homeData.trending && <Trending trending={homeData.trending} />}

      {/* Main content layout with sidebar */}
      <div className="flex flex-col lg:flex-row gap-8 mt-8">

        {/* Main Content Area (Larger Section) */}
        <main className="flex-grow lg:w-3/4 space-y-12">
          {homeData.latest_episode && (
            <CategoryCard
              label="Latest Episodes"
              data={homeData.latest_episode}
              path="latest-episodes" // Example path for "View more" link
            />
          )}
          {homeData.latest_completed && (
            <CategoryCard
              label="Recently Completed"
              data={homeData.latest_completed}
              path="completed" // Example path for "View more" link
            />
          )}
        </main>

        {/* Sidebar (Smaller Section) */}
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
