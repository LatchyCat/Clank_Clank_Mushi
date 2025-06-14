// mushi-frontend/src/components/data/DataIngestionControls.jsx
import React, { useState } from 'react';
import { api } from '../../services/api'; // Correct path to api.js

/**
 * DataIngestionControls component provides UI to trigger data ingestion processes.
 * This component is intended for admin use only.
 */
function DataIngestionControls() {
  const [ingestAllLoading, setIngestAllLoading] = useState(false);
  const [ingestAllMessage, setIngestAllMessage] = useState('');
  const [ingestAllError, setIngestAllError] = useState('');

  const [ingestCategoryLoading, setIngestCategoryLoading] = useState(false);
  const [ingestCategoryMessage, setIngestCategoryMessage] = useState('');
  const [ingestCategoryError, setIngestCategoryError] = useState('');
  const [categoriesInput, setCategoriesInput] = useState('action,comedy,fantasy'); // Default categories
  const [limitPerCategoryInput, setLimitPerCategoryInput] = useState(50); // Default limit

  const handleIngestAllData = async () => {
    setIngestAllLoading(true);
    setIngestAllMessage('');
    setIngestAllError('');
    try {
      const response = await api.data.ingestAllData();
      if (response && response.message) {
        setIngestAllMessage(`Success! ${response.message} ✨`);
      } else {
        setIngestAllError("Eeeh~ Mushi didn't get a clear success message after ingesting all data. (T_T)");
      }
    } catch (err) {
      console.error("Uwaah! Failed to ingest all data:", err);
      setIngestAllError(`Mushi encountered an error while ingesting all data: ${err.message || "Unknown error"} (>_<)`);
    } finally {
      setIngestAllLoading(false);
    }
  };

  const handleIngestAnimeApiCategoryData = async () => {
    setIngestCategoryLoading(true);
    setIngestCategoryMessage('');
    setIngestCategoryError('');

    const categories = categoriesInput.split(',').map(c => c.trim()).filter(c => c !== '');
    const limit = parseInt(limitPerCategoryInput, 10);

    if (categories.length === 0) {
      setIngestCategoryError("Senpai, Mushi needs at least one category to ingest! (•́-•̀)");
      setIngestCategoryLoading(false);
      return;
    }
    if (isNaN(limit) || limit <= 0) {
      setIngestCategoryError("Senpai, the limit per category must be a positive number! (•́-•̀)");
      setIngestCategoryLoading(false);
      return;
    }

    try {
      const response = await api.data.ingestAnimeApiCategoryData(categories.join(','), limit);
      if (response && response.message) {
        setIngestCategoryMessage(`Success! ${response.message} ✨`);
      } else {
        setIngestCategoryError("Eeeh~ Mushi didn't get a clear success message after ingesting category data. (T_T)");
      }
    } catch (err) {
      console.error("Uwaah! Failed to ingest category data:", err);
      setIngestCategoryError(`Mushi encountered an error while ingesting category data: ${err.message || "Unknown error"} (>_<)`);
    } finally {
      setIngestCategoryLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Mushi's Data Ingestion Controls! (ﾉ´ヮ´)ﾉ*:･ﾟ✧
      </h2>

      {/* Ingest All Data Section */}
      <section className="mb-12 p-6 bg-gray-800 rounded-lg shadow-xl border border-indigo-600 max-w-2xl mx-auto">
        <h3 className="text-2xl font-bold text-indigo-400 mb-4">Ingest All Data Sources~</h3>
        <p className="text-gray-300 mb-4">
          This will fetch and embed data from all configured sources (One Piece, ANN, Anime API, etc.) into the vector store. This might take a while, desu!
        </p>
        <button
          onClick={handleIngestAllData}
          disabled={ingestAllLoading}
          className="px-6 py-3 bg-blue-600 text-white font-bold text-lg rounded-full shadow-lg
                     hover:bg-blue-700 transform hover:scale-105 transition-all duration-300
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {ingestAllLoading ? "Mushi is working hard... ✨" : "Ingest All Data!~"}
        </button>
        {ingestAllMessage && <p className="text-green-400 mt-4 text-sm">{ingestAllMessage}</p>}
        {ingestAllError && <p className="text-red-400 mt-4 text-sm">{ingestAllError}</p>}
      </section>

      {/* Ingest Anime API Category Data Section */}
      <section className="p-6 bg-gray-800 rounded-lg shadow-xl border border-indigo-600 max-w-2xl mx-auto">
        <h3 className="text-2xl font-bold text-indigo-400 mb-4">Ingest Anime API Category Data~</h3>
        <p className="text-gray-300 mb-4">
          This will fetch and embed anime data for specific categories from the 'anime-api' Node.js project.
        </p>
        <div className="mb-4">
          <label htmlFor="categoriesInput" className="block text-gray-300 text-sm font-medium mb-2">
            Categories (comma-separated slugs, e.g., action,comedy):
          </label>
          <input
            id="categoriesInput"
            type="text"
            value={categoriesInput}
            onChange={(e) => setCategoriesInput(e.target.value)}
            placeholder="action,comedy,genre/fantasy"
            className="w-full p-3 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="limitInput" className="block text-gray-300 text-sm font-medium mb-2">
            Limit Per Category (e.g., 50):
          </label>
          <input
            id="limitInput"
            type="number"
            min="1"
            value={limitPerCategoryInput}
            onChange={(e) => setLimitPerCategoryInput(e.target.value)}
            placeholder="50"
            className="w-full p-3 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <button
          onClick={handleIngestAnimeApiCategoryData}
          disabled={ingestCategoryLoading}
          className="px-6 py-3 bg-blue-600 text-white font-bold text-lg rounded-full shadow-lg
                     hover:bg-blue-700 transform hover:scale-105 transition-all duration-300
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {ingestCategoryLoading ? "Mushi is collecting anime... ✨" : "Ingest Category Data!~"}
        </button>
        {ingestCategoryMessage && <p className="text-green-400 mt-4 text-sm">{ingestCategoryMessage}</p>}
        {ingestCategoryError && <p className="text-red-400 mt-4 text-sm">{ingestCategoryError}</p>}
      </section>
    </div>
  );
}

export default DataIngestionControls;
