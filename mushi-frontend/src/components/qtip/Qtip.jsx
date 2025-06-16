import React from 'react';
import AnimeQuickInfoCard from '../anime/AnimeQuickInfoCard';

// This component acts as a wrapper for the quick info card.
function Qtip({ id }) {
  if (!id) return null;
  return <AnimeQuickInfoCard qtipId={id} />;
}

export default Qtip;
