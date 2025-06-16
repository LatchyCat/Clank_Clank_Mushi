import React from 'react';
import { Link } from 'react-router-dom';
import { X, Home, Bot, Search, Database, ShieldCheck, List } from 'lucide-react';

const mainLinks = [
  { to: '/home', label: 'Home', icon: <Home size={20} /> },
  { to: '/mushi_ai', label: 'Mushi AI', icon: <Bot size={20} /> },
  { to: '/search', label: 'Anime Search', icon: <Search size={20} /> },
  { to: '/az-list', label: 'A-Z List', icon: <List size={20} /> }
];

const toolLinks = [
  { to: '/data_insights', label: 'Data Insights', icon: <Database size={20} /> },
  { to: '/admin_data', label: 'Admin Panel', icon: <ShieldCheck size={20} /> }
];

const Sidebar = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 bg-black transition-opacity duration-300 ease-in-out z-[99] ${
          isOpen ? 'bg-opacity-60' : 'bg-opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />
      {/* Sidebar Panel */}
      <aside
        className={`fixed top-0 left-0 h-full w-72 bg-neutral-900 text-foreground shadow-2xl transform transition-transform duration-300 ease-in-out z-[100] flex flex-col p-6 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex justify-between items-center mb-8">
          <Link to="/home" onClick={onClose} className="text-white text-2xl font-extrabold hover:text-pink-300 transition-colors duration-300">
            Clank Clank Mushi
          </Link>
          <button onClick={onClose} className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-white/10" aria-label="Close menu">
            <X size={24} />
          </button>
        </div>

        <nav className="flex flex-col gap-y-2 flex-grow">
          {/* Main Navigation */}
          {mainLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={onClose}
              className="flex items-center gap-4 px-4 py-3 text-lg font-medium text-gray-300 rounded-lg hover:bg-purple-600/30 hover:text-white transition-colors"
            >
              {link.icon}
              <span>{link.label}</span>
            </Link>
          ))}

          {/* Divider */}
          <hr className="my-6 border-white/10" />

          {/* Tools Section */}
          <h3 className="px-4 text-sm font-semibold text-muted-foreground uppercase tracking-wider">Tools</h3>
          {toolLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={onClose}
              className={`flex items-center gap-4 px-4 py-3 text-lg font-medium rounded-lg transition-colors ${
                link.to === '/admin_data'
                  ? 'text-yellow-400 hover:bg-yellow-500/20'
                  : 'text-gray-300 hover:bg-purple-600/30 hover:text-white'
              }`}
            >
              {link.icon}
              <span>{link.label}</span>
            </Link>
          ))}
        </nav>

        <footer className="mt-auto text-center text-xs text-muted-foreground">
          <p>© {new Date().getFullYear()} Clank Clank Mushi</p>
        </footer>
      </aside>
    </>
  );
};

export default Sidebar;
