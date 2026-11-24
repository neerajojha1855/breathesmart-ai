import React, { useEffect, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity,
  Bot,
  CalendarCheck,
  Compass,
  Home,
  Leaf,
  Loader2,
  MapPin,
  Menu,
  Search,
  User,
  X,
} from 'lucide-react';
import { useLocation } from '../../hooks/useLocation';
import { api } from '../../services/api';
import type { LocationSearchResult } from '../../types';

export const Navbar: React.FC = () => {
  const { location, setLocation, requestGPSLocation, isLocating, gpsError } = useLocation();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LocationSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await api.searchLocations(searchQuery);
        setSearchResults(results);
      } catch {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setIsSearchOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: Activity },
    { to: '/planner', label: 'Daily Planner', icon: CalendarCheck },
    { to: '/indoor', label: 'Indoor Air', icon: Home },
    { to: '/sustainability', label: 'Sustainability', icon: Leaf },
    { to: '/assistant', label: 'AI Assistant', icon: Bot },
    { to: '/profile', label: 'Preferences', icon: User },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-3 group focus-visible:ring-emerald-500">
            <img src="/logo.svg" alt="BreatheSmart AI Logo" className="h-9 w-auto" />
          </NavLink>

          {/* Location Picker & Quick Switcher */}
          <div className="relative" ref={searchRef}>
            <button
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors focus-visible:ring-2 focus-visible:ring-emerald-500"
              aria-expanded={isSearchOpen}
              aria-label={`Current location: ${location.city}. Click to change.`}
            >
              <MapPin className="w-4 h-4 text-emerald-600" />
              <span className="max-w-[130px] sm:max-w-[180px] truncate">{location.city}</span>
            </button>

            {/* Dropdown Search Popover */}
            {isSearchOpen && (
              <div className="absolute left-0 sm:right-0 sm:left-auto mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 p-3 z-50 animate-in fade-in slide-in-from-top-2">
                <div className="relative mb-2">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search city e.g. London, Tokyo..."
                    className="w-full pl-9 pr-3 py-1.5 text-sm rounded-lg border border-slate-300 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                    autoFocus
                  />
                </div>

                <button
                  onClick={() => {
                    requestGPSLocation();
                    setIsSearchOpen(false);
                  }}
                  disabled={isLocating}
                  className="w-full flex items-center justify-center gap-2 py-1.5 mb-2 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors"
                >
                  {isLocating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Compass className="w-3.5 h-3.5" />}
                  Use My Current GPS Coordinates
                </button>

                {gpsError && <p className="text-xs text-rose-600 mb-2 px-1">{gpsError}</p>}

                {isSearching && (
                  <div className="flex items-center justify-center py-4 text-xs text-slate-500">
                    <Loader2 className="w-4 h-4 animate-spin mr-2" /> Searching cities...
                  </div>
                )}

                {searchResults.length > 0 && (
                  <ul className="max-h-56 overflow-y-auto divide-y divide-slate-100">
                    {searchResults.map((res) => (
                      <li key={res.id || `${res.latitude}-${res.longitude}`}>
                        <button
                          onClick={() => {
                            setLocation({
                              city: res.name,
                              country: res.country,
                              latitude: res.latitude,
                              longitude: res.longitude,
                            });
                            setIsSearchOpen(false);
                            setSearchQuery('');
                          }}
                          className="w-full text-left px-2 py-2 text-xs hover:bg-slate-50 rounded flex justify-between items-center"
                        >
                          <div>
                            <span className="font-semibold text-slate-800">{res.name}</span>
                            {res.admin1 && <span className="text-slate-500 ml-1">({res.admin1})</span>}
                            <div className="text-[11px] text-slate-400">{res.country}</div>
                          </div>
                          <span className="text-[10px] text-slate-400">
                            {res.latitude.toFixed(2)}, {res.longitude.toFixed(2)}
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
            {navLinks.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {label}
              </NavLink>
            ))}
          </nav>

          {/* Mobile Hamburger Toggle */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              aria-label={mobileMenuOpen ? 'Close Menu' : 'Open Menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {navLinks.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-base font-medium ${
                  isActive
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </div>
      )}
    </header>
  );
};
