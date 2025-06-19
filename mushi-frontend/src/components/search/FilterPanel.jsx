// mushi-frontend/src/components/search/FilterPanel.jsx (NEW FILE)
import React, { useState, useEffect } from 'react';
import CustomDropdown from '@/components/common/CustomDropdown';
import { categoryGroups } from '@/services/categories';
import { filterOptions } from '@/services/filterOptions';
import { Search } from 'lucide-react';

const FilterPanel = ({ initialFilters, onFilterSubmit }) => {
    const [selectedGenres, setSelectedGenres] = useState(initialFilters.genres || []);
    const [selectedType, setSelectedType] = useState(initialFilters.type || 'all');
    const [selectedStatus, setSelectedStatus] = useState(initialFilters.status || 'all');
    const [selectedRated, setSelectedRated] = useState(initialFilters.rated || 'all');
    const [selectedScore, setSelectedScore] = useState(initialFilters.score || 'all');
    const [selectedSeason, setSelectedSeason] = useState(initialFilters.season || 'all');
    const [selectedLanguage, setSelectedLanguage] = useState(initialFilters.language || 'all');
    const [selectedSort, setSelectedSort] = useState(initialFilters.sort || 'default');

    // Update state if initialFilters from URL change
    useEffect(() => {
        setSelectedGenres(initialFilters.genres || []);
        setSelectedType(initialFilters.type || 'all');
        setSelectedStatus(initialFilters.status || 'all');
        setSelectedRated(initialFilters.rated || 'all');
        setSelectedScore(initialFilters.score || 'all');
        setSelectedSeason(initialFilters.season || 'all');
        setSelectedLanguage(initialFilters.language || 'all');
        setSelectedSort(initialFilters.sort || 'default');
    }, [initialFilters]);


    const handleGenreToggle = (genreSlug) => {
        setSelectedGenres(prev =>
            prev.includes(genreSlug)
                ? prev.filter(g => g !== genreSlug)
                : [...prev, genreSlug]
        );
    };

    const handleSubmit = () => {
        const filters = {
            genres: selectedGenres,
            type: selectedType,
            status: selectedStatus,
            rated: selectedRated,
            score: selectedScore,
            season: selectedSeason,
            language: selectedLanguage,
            sort: selectedSort,
        };
        onFilterSubmit(filters);
    };

    return (
        <div className="bg-neutral-800/60 p-6 rounded-2xl border border-white/10">
            {/* Breadcrumbs */}
            <div className="mb-6">
                <p className="text-sm text-gray-400">
                    <span className="hover:text-white cursor-pointer">Home</span>
                    <span className="mx-2">•</span>
                    <span className="text-white">Filter</span>
                </p>
            </div>

            {/* Top Filters */}
            <h3 className="text-lg font-bold text-white mb-4">Filter</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
                <CustomDropdown label="Type" options={filterOptions.type} selectedValue={selectedType} onSelect={setSelectedType} />
                <CustomDropdown label="Status" options={filterOptions.status} selectedValue={selectedStatus} onSelect={setSelectedStatus} />
                <CustomDropdown label="Rated" options={filterOptions.rated} selectedValue={selectedRated} onSelect={setSelectedRated} />
                <CustomDropdown label="Score" options={filterOptions.score} selectedValue={selectedScore} onSelect={setSelectedScore} />
                <CustomDropdown label="Season" options={filterOptions.season} selectedValue={selectedSeason} onSelect={setSelectedSeason} />
                <CustomDropdown label="Language" options={filterOptions.language} selectedValue={selectedLanguage} onSelect={setSelectedLanguage} />
                <CustomDropdown label="Sort" options={filterOptions.sort} selectedValue={selectedSort} onSelect={setSelectedSort} />
            </div>

            {/* Genres */}
            <h3 className="text-lg font-bold text-white mb-4">Genre</h3>
            <div className="flex flex-wrap gap-2 mb-8">
                {categoryGroups.genres.items.map(genre => (
                    <button
                        key={genre.slug}
                        onClick={() => handleGenreToggle(genre.slug)}
                        className={`px-3 py-1.5 text-sm rounded-full border transition-all duration-200 ${
                            selectedGenres.includes(genre.slug)
                                ? 'bg-pink-500 border-pink-500 text-black font-semibold'
                                : 'bg-neutral-700/50 border-neutral-600 text-gray-300 hover:bg-neutral-600/50'
                        }`}
                    >
                        {genre.name}
                    </button>
                ))}
            </div>

            <div className="flex justify-end">
                <button
                    onClick={handleSubmit}
                    className="flex items-center gap-2 bg-yellow-400 text-black font-bold px-8 py-3 rounded-lg hover:bg-yellow-300 transition-colors transform hover:scale-105"
                >
                    <Search size={18}/>
                    Filter
                </button>
            </div>
        </div>
    );
};

export default FilterPanel;
