// mushi-frontend/src/components/anime/searchbar/PageSpecificSearchBar.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import useSearch from '@/components/hooks/useSearch';
import Suggestion from './Suggestion';

function PageSpecificSearchBar() {
    const navigate = useNavigate();
    const {
        searchValue,
        setSearchValue,
        isFocused,
        setIsFocused,
        debouncedValue,
        suggestionRef,
        handleBlur,
        clearSearch
    } = useSearch();

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        if (searchValue.trim()) {
            navigate(`/search?keyword=${encodeURIComponent(searchValue)}`);
            // We can clear the search on submit here too, for a cleaner experience
            clearSearch();
        }
    };

    const handleSuggestionClick = () => {
        clearSearch();
    };

    return (
        <div className="w-full max-w-2xl mx-auto my-12 relative">
            <h1 className="text-4xl md:text-5xl font-extrabold text-center mb-6 bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400 drop-shadow-lg [text-shadow:0_0_10px_rgba(255,100,255,0.2)]">
                Explore the Anime Universe
            </h1>
            <p className="text-center text-lg text-muted-foreground mb-8">
                Find your next favorite series or browse our categories below.
            </p>
            <form onSubmit={handleSearchSubmit} className="relative">
                <input
                    type="text"
                    className="w-full py-4 pl-14 pr-6 rounded-full bg-neutral-800/80 backdrop-blur-sm border-2 border-purple-500/30 text-white placeholder-gray-400 text-lg focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-300 shadow-lg"
                    placeholder="Search for an anime, like 'Frieren'..."
                    value={searchValue}
                    onChange={(e) => setSearchValue(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={handleBlur}
                />
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-purple-400 pointer-events-none" />
            </form>

            {isFocused && debouncedValue && (
                <div ref={suggestionRef} className="absolute w-full mt-2 z-50">
                    <Suggestion keyword={debouncedValue} onSuggestionClick={handleSuggestionClick} />
                </div>
            )}
        </div>
    );
}

export default PageSpecificSearchBar;
