// mushi-frontend/src/components/common/CustomDropdown.jsx (NEW FILE)
import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

const CustomDropdown = ({ label, options, selectedValue, onSelect }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    const selectedLabel = options.find(opt => opt.value === selectedValue)?.label || 'All';

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (value) => {
        onSelect(value);
        setIsOpen(false);
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center justify-between w-full px-4 py-2 text-left bg-neutral-700/50 border border-neutral-600 rounded-lg hover:bg-neutral-600/70 transition-colors"
            >
                <span className="text-gray-400">{label}: <span className="text-white font-medium">{selectedLabel}</span></span>
                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
                <div className="absolute top-full mt-2 w-full max-h-60 overflow-y-auto bg-neutral-800 border border-neutral-700 rounded-lg shadow-xl z-20">
                    <ul className="p-1">
                        {options.map(option => (
                            <li key={option.value}>
                                <button
                                    onClick={() => handleSelect(option.value)}
                                    className={`w-full text-left px-3 py-2 text-sm rounded-md ${selectedValue === option.value ? 'bg-purple-600 text-white' : 'text-gray-300 hover:bg-white/10'}`}
                                >
                                    {option.label}
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default CustomDropdown;
