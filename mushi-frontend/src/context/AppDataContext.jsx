// mushi-frontend/src/context/AppDataContext.jsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import { api } from '@/services/api';

const AppDataContext = createContext(null);

export const useAppData = () => useContext(AppDataContext);

export const AppDataProvider = ({ children }) => {
    const [homeData, setHomeData] = useState(null);
    const [menuData, setMenuData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // This effect runs only once when the app loads, fetching all initial data.
        const fetchInitialData = async () => {
            console.log("Mushi is fetching initial app data for caching...");
            try {
                // A single, consolidated API call for all homepage data
                const homeDataResponse = await api.anime.getHomeData();
                if (homeDataResponse) {
                    setHomeData(homeDataResponse);

                    // Derive the menu data from the already-fetched home data.
                    const genresForMenu = [
                        { name: 'Action', slug: 'action' }, { name: 'Adventure', slug: 'adventure' },
                        { name: 'Comedy', slug: 'comedy' }, { name: 'Drama', slug: 'drama' },
                        { name: 'Sci-Fi', slug: 'sci-fi' }, { name: 'Fantasy', slug: 'fantasy' },
                    ];

                    const derivedMenuData = {
                        trending: homeDataResponse.trending?.slice(0, 5) || [],
                        topAiring: homeDataResponse.top_airing?.slice(0, 5) || [],
                        mostPopular: homeDataResponse.most_popular?.slice(0, 3) || [],
                        genres: genresForMenu,
                    };
                    setMenuData(derivedMenuData);
                    console.log("Mushi has successfully cached the initial data, Senpai!");
                } else {
                    throw new Error("Mushi couldn't fetch home data.");
                }
            } catch (err) {
                console.error("Uwaah! Failed to fetch and cache initial app data:", err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchInitialData();
    }, []); // Empty dependency array ensures this runs only ONCE.

    const value = {
        homeData,
        menuData,
        isLoading,
        error
    };

    return (
        <AppDataContext.Provider value={value}>
            {children}
        </AppDataContext.Provider>
    );
};
