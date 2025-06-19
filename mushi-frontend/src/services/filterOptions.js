// mushi-frontend/src/services/filterOptions.js

export const filterOptions = {
    type: [
        { value: 'all', label: 'All' },
        { value: 'tv', label: 'TV' },
        { value: 'movie', label: 'Movie' },
        { value: 'ova', label: 'OVA' },
        { value: 'ona', label: 'ONA' },
        { value: 'special', label: 'Special' },
    ],
    status: [
        { value: 'all', label: 'All' },
        { value: 'airing', label: 'Currently Airing' },
        { value: 'completed', label: 'Completed' },
        { value: 'upcoming', label: 'Upcoming' },
    ],
    rated: [
        { value: 'all', label: 'All' },
        { value: 'g', label: 'G - All Ages' },
        { value: 'pg', label: 'PG - Children' },
        { value: 'pg-13', label: 'PG-13' },
        { value: 'r-17', label: 'R - 17+' },
        { value: 'r', label: 'R+ - Mild Nudity' },
    ],
    score: [
        { value: 'all', label: 'All' },
        { value: '9', label: '(9) Masterpiece' },
        { value: '8', label: '(8) Great' },
        { value: '7', label: '(7) Good' },
        { value: '6', label: '(6) Fine' },
        { value: '5', label: '(5) Average' },
    ],
    season: [
        { value: 'all', label: 'All' },
        { value: 'spring', label: 'Spring' },
        { value: 'summer', label: 'Summer' },
        { value: 'fall', label: 'Fall' },
        { value: 'winter', label: 'Winter' },
    ],
    language: [
        { value: 'all', label: 'All' },
        { value: 'sub', label: 'Subbed' },
        { value: 'dub', label: 'Dubbed' },
        { value: 'subdub', label: 'Sub & Dub' },
    ],
    sort: [
        { value: 'default', label: 'Default' },
        { value: 'updated_at', label: 'Recently Updated' },
        { value: 'created_at', label: 'Recently Added' },
        { value: 'title_asc', label: 'Title (A-Z)' },
        { value: 'title_desc', label: 'Title (Z-A)' },
        { value: 'score', label: 'Highest Score' },
        { value: 'most_viewed', label: 'Most Viewed' },
    ],
};
