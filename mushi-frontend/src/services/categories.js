// mushi-frontend/src/services/categories.js

/**
 * A structured list of categories for the UI on the search page.
 * The 'slug' corresponds to the path parameter required by the backend API.
 * The 'name' is the user-friendly text displayed on the button/link.
 */
export const categoryGroups = {
  main: {
    title: 'Top Lists',
    items: [
      { slug: 'top-airing', name: 'Top Airing' },
      { slug: 'most-popular', name: 'Most Popular' },
      { slug: 'most-favorite', name: 'Most Favorite' },
      { slug: 'completed', name: 'Completed' },
      { slug: 'recently-updated', name: 'Recently Updated' },
      { slug: 'recently-added', name: 'Recently Added' },
      { slug: 'top-upcoming', name: 'Top Upcoming' },
    ],
  },
  standard: {
    title: 'Type',
    items: [
      { slug: 'subbed-anime', name: 'Subbed' },
      { slug: 'dubbed-anime', name: 'Dubbed' },
      { slug: 'movie', name: 'Movies' },
      { slug: 'special', name: 'Specials' },
      { slug: 'ova', name: 'OVA' },
      { slug: 'ona', name: 'ONA' },
      { slug: 'tv', name: 'TV' },
    ],
  },
  genres: {
    title: 'Genres',
    items: [
      { slug: 'genre/action', name: 'Action' },
      { slug: 'genre/adventure', name: 'Adventure' },
      { slug: 'genre/cars', name: 'Cars' },
      { slug: 'genre/comedy', name: 'Comedy' },
      { slug: 'genre/dementia', name: 'Dementia' },
      { slug: 'genre/demons', name: 'Demons' },
      { slug: 'genre/drama', name: 'Drama' },
      { slug: 'genre/ecchi', name: 'Ecchi' },
      { slug: 'genre/fantasy', name: 'Fantasy' },
      { slug: 'genre/game', name: 'Game' },
      { slug: 'genre/harem', name: 'Harem' },
      { slug: 'genre/historical', name: 'Historical' },
      { slug: 'genre/horror', name: 'Horror' },
      { slug: 'genre/isekai', name: 'Isekai' },
      { slug: 'genre/josei', name: 'Josei' },
      { slug: 'genre/kids', name: 'Kids' },
      { slug: 'genre/magic', name: 'Magic' },
      { slug: 'genre/martial-arts', name: 'Martial Arts' },
      { slug: 'genre/mecha', name: 'Mecha' },
      { slug: 'genre/military', name: 'Military' },
      { slug: 'genre/music', name: 'Music' },
      { slug: 'genre/mystery', name: 'Mystery' },
      { slug: 'genre/parody', name: 'Parody' },
      { slug: 'genre/police', name: 'Police' },
      { slug: 'genre/psychological', name: 'Psychological' },
      { slug: 'genre/romance', name: 'Romance' },
      { slug: 'genre/samurai', name: 'Samurai' },
      { slug: 'genre/school', name: 'School' },
      { slug: 'genre/sci-fi', name: 'Sci-Fi' },
      { slug: 'genre/seinen', name: 'Seinen' },
      { slug: 'genre/shoujo', name: 'Shoujo' },
      { slug: 'genre/shoujo-ai', name: 'Shoujo-ai' },
      { slug: 'genre/shounen', name: 'Shounen' },
      { slug: 'genre/shounen-ai', name: 'Shounen-ai' },
      { slug: 'genre/slice-of-life', name: 'Slice of Life' },
      { slug: 'genre/space', name: 'Space' },
      { slug: 'genre/sports', name: 'Sports' },
      { slug: 'genre/super-power', name: 'Super Power' },
      { slug: 'genre/supernatural', name: 'Supernatural' },
      { slug: 'genre/thriller', name: 'Thriller' },
      { slug: 'genre/vampire', name: 'Vampire' },
    ],
  },
};
