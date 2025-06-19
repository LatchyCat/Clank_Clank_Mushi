// src/hooks/useSearch.js
import { useState, useRef } from 'react';
import useDebounce from './useDebounce'; // Import our new debounce hook

export default function useSearch() {
  const [searchValue, setSearchValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const debouncedValue = useDebounce(searchValue, 300); // 300ms delay

  const suggestionRef = useRef(null);

  const handleBlur = () => {
    setTimeout(() => {
      if (suggestionRef.current && !suggestionRef.current.contains(document.activeElement)) {
        setIsFocused(false);
      }
    }, 150);
  };

  const clearSearch = () => {
    setSearchValue('');
    setIsFocused(false);
  };

  return {
    searchValue,
    setSearchValue,
    isFocused,
    setIsFocused,
    debouncedValue,
    suggestionRef,
    handleBlur,
    clearSearch, // Export the new function
  };
}
