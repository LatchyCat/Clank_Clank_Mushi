// mushi-frontend/src/components/TopNav.jsx
import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Home, MessageSquare, Database } from 'lucide-react'; // Icons for visual flair

function TopNav() {
  // Style for the active NavLink
  const activeLinkStyle = {
    color: '#60a5fa', // A light blue color for the active link
    borderBottom: '2px solid #60a5fa',
  };

  return (
    <nav className="bg-gray-800 p-4 shadow-lg sticky top-0 z-50">
      <ul className="flex justify-center items-center space-x-10">
        <li>
          <NavLink
            to="/app"
            end // 'end' ensures this only matches /app, not /app/chat etc.
            style={({ isActive }) => (isActive ? activeLinkStyle : undefined)}
            className="flex items-center text-xl font-bold text-gray-200 hover:text-blue-400 transition-all duration-200 pb-1"
          >
            <Home className="mr-2" size={22} />
            Home
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/app/chat"
            style={({ isActive }) => (isActive ? activeLinkStyle : undefined)}
            className="flex items-center text-xl font-bold text-gray-200 hover:text-blue-400 transition-all duration-200 pb-1"
          >
            <MessageSquare className="mr-2" size={22} />
            Chat with Mushi
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/app/data"
            style={({ isActive }) => (isActive ? activeLinkStyle : undefined)}
            className="flex items-center text-xl font-bold text-gray-200 hover:text-blue-400 transition-all duration-200 pb-1"
          >
            <Database className="mr-2" size={22} />
            Data Explorer
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}

export default TopNav;
