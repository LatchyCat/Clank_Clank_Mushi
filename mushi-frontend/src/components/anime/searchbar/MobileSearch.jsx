import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useNavigate } from "react-router-dom";
import useSearch from '@/components/hooks/useSearch';
import Suggestion from "./Suggestion";

function MobileSearch() {
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

    const handleSearchSubmit = () => {
        if (searchValue.trim()) {
            navigate(`/search?keyword=${encodeURIComponent(searchValue)}`);
            setIsFocused(false);
        }
    };

    return (
        <div className="relative w-full max-w-sm mx-auto">
            <div className="flex items-center">
                <input
                    type="text"
                    className="bg-white/10 border border-white/20 text-white rounded-l-full py-2 px-4 focus:outline-none focus:ring-2 focus:ring-pink-400 w-full"
                    placeholder="Search anime..."
                    value={searchValue}
                    onChange={(e) => setSearchValue(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={handleBlur}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
                />
                <button
                    className="bg-pink-500 hover:bg-pink-600 p-3 rounded-r-full text-white"
                    onClick={handleSearchSubmit}
                    aria-label="Search"
                >
                    <FontAwesomeIcon icon={faMagnifyingGlass} />
                </button>
            </div>
            {isFocused && debouncedValue && (
                <div ref={suggestionRef}>
                    <Suggestion keyword={debouncedValue} onSuggestionClick={clearSearch} />
                </div>
            )}
        </div>
    );
}

export default MobileSearch;
