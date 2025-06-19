// src/main.jsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { LanguageProvider } from './context/LanguageContext.jsx';
import { AppDataProvider } from './context/AppDataContext.jsx'; // <-- Import the new provider

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <LanguageProvider>
      <AppDataProvider> {/* <-- Wrap the App */}
        <App />
      </AppDataProvider>
    </LanguageProvider>
  </React.StrictMode>
);
