// src/hooks/useSearch.js (NEW FILE)
import { useState, useRef } from 'react';
import useDebounce from './useDebounce'; // Import our new debounce hook

export default function useSearch() {
  const [searchValue, setSearchValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const debouncedValue = useDebounce(searchValue, 300); // 300ms delay

  const suggestionRef = useRef(null);

  // This function will be passed to the onBlur handler of the input
  const handleBlur = () => {
    // We delay the blur event slightly to allow a click on the suggestion box
    // to register before the input loses focus and hides the suggestions.
    setTimeout(() => {
      // If the currently focused element is NOT inside the suggestion box, hide it.
      if (suggestionRef.current && !suggestionRef.current.contains(document.activeElement)) {
        setIsFocused(false);
      }
    }, 150);
  };

  return {
    searchValue,
    setSearchValue,
    isFocused,
    setIsFocused,
    debouncedValue,
    suggestionRef,
    handleBlur,
  };
}
