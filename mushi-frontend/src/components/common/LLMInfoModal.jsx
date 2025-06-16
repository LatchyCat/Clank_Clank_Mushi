// mushi-frontend/src/components/llm/ProviderSelector.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api'; // This correctly imports the 'api' object from its separate file

function ProviderSelector() {
  const [providers, setProviders] = useState({});
  // Initialize selectedProvider to the desired default ('ollama_anime').
  // It will be updated by the API call if a different provider is currently active on the backend.
  const [selectedProvider, setSelectedProvider] = useState('ollama_anime');
  const [feedback, setFeedback] = useState('');
  const [isLoading, setIsLoading] = useState(true); // New loading state

  // Fetch the available providers and the current selected provider when the component mounts
  useEffect(() => {
    const fetchLLMInfo = async () => {
      setIsLoading(true); // Start loading
      try {
        // Fetch all available providers
        const providerData = await api.llm.getProviders();
        setProviders(providerData);

        // Fetch the currently selected provider from the backend
        const currentProviderResponse = await api.llm.getCurrentProvider();

        // If the backend successfully returns a current provider, use it.
        // Otherwise, stick with our initial default ('ollama_anime').
        if (currentProviderResponse && currentProviderResponse.current_provider) {
          setSelectedProvider(currentProviderResponse.current_provider);
        } else {
          // If backend did not return a specific current provider,
          // the component will remain at its initialized 'ollama_anime' state.
          console.warn("Backend did not return a specific current LLM provider. Displaying initial default.");
        }
      } catch (error) {
        console.error('Failed to load LLM providers or current provider:', error);
        setFeedback('Failed to load LLM providers or current provider.');
        // If there's an error fetching, the component will remain at its initialized 'ollama_anime' state.
        // No explicit setSelectedProvider('ollama_anime') needed here as it's the initial state.
      } finally {
        setIsLoading(false); // End loading
      }
    };
    fetchLLMInfo();
  }, []); // Empty dependency array means this effect runs once on mount

  const handleProviderChange = async (event) => {
    const newProvider = event.target.value;
    setSelectedProvider(newProvider); // Optimistically update UI
    setFeedback('Setting provider...');
    try {
      const result = await api.llm.setProvider(newProvider);
      setFeedback(result.message); // e.g., "LLM provider set to ollama_anime"
    } catch (error) {
      console.error('Failed to set LLM provider:', error);
      setFeedback(`Error setting provider: ${error.message || 'Unknown error'}`);
    }
  };

  return (
    <div className="bg-white/5 p-4 rounded-xl shadow-lg mb-4 border border-white/10"> {/* Softened background, rounded, shadow, border */}
      <label htmlFor="llm-provider" className="block text-sm font-medium text-gray-300 mb-2">
        Choose LLM Provider
      </label>
      {isLoading ? (
        <p className="text-gray-400">Loading providers...</p>
      ) : (
        <select
          id="llm-provider"
          value={selectedProvider}
          onChange={handleProviderChange}
          className="w-full bg-white/10 border border-white/20 rounded-lg p-2 text-white focus:ring-2 focus:ring-pink-500" // Softened background, border, focus ring
          disabled={Object.keys(providers).length === 0}
        >
          {/* The "Select a provider" option is now less likely to be seen if selectedProvider defaults correctly.
              It serves as a fallback if selectedProvider is somehow an empty string,
              or if no options are available. */}
          <option value="" disabled>Select a provider</option>
          {Object.entries(providers).map(([key, name]) => (
            <option key={key} value={key}>
              {name}
            </option>
          ))}
        </select>
      )}
      {feedback && <p className="text-xs text-gray-400 mt-2">{feedback}</p>}
    </div>
  );
}

export default ProviderSelector;
