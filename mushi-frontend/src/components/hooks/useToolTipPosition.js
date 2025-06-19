import { useState, useEffect, useCallback } from 'react';

const useToolTipPosition = (hoveredItemId, cardRefs) => {
    const [tooltipStyle, setTooltipStyle] = useState({
        opacity: 0,
        position: 'fixed', // Use fixed positioning to handle scroll
        transition: 'opacity 0.2s ease-in-out, transform 0.2s ease-in-out',
        transform: 'translateY(10px)',
        pointerEvents: 'none', // Prevent tooltip from capturing mouse events
        zIndex: 100000,
    });

    const calculatePosition = useCallback(() => {
        if (!hoveredItemId || !cardRefs.current[hoveredItemId]) {
            return;
        }

        const cardElement = cardRefs.current[hoveredItemId];
        const cardRect = cardElement.getBoundingClientRect();
        const viewportWidth = window.innerWidth;

        const tooltipWidth = 320; // Corresponds to w-80 in Tailwind for the Qtip card
        const space = 15; // Space between card and tooltip

        let left;

        // Horizontal positioning: prefer right, fallback to left
        if (cardRect.right + tooltipWidth + space < viewportWidth) {
            // Enough space on the right
            left = cardRect.right + space;
        } else {
            // Place on the left
            left = cardRect.left - tooltipWidth - space;
        }

        setTooltipStyle(prev => ({
            ...prev,
            top: cardRect.top, // Use fixed positioning relative to viewport
            left: left,
            opacity: 1,
            transform: 'translateY(0)',
        }));
    }, [hoveredItemId, cardRefs]);

    useEffect(() => {
        if (hoveredItemId) {
            calculatePosition();
            // Recalculate on scroll and resize to keep it pinned correctly
            window.addEventListener('scroll', calculatePosition, true);
            window.addEventListener('resize', calculatePosition);
        } else {
            setTooltipStyle(prev => ({
                ...prev,
                opacity: 0,
                transform: 'translateY(10px)',
            }));
        }

        return () => {
            window.removeEventListener('scroll', calculatePosition, true);
            window.removeEventListener('resize', calculatePosition);
        };
    }, [hoveredItemId, calculatePosition]);

    return { tooltipStyle };
};

export default useToolTipPosition;
