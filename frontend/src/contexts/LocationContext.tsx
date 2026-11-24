import React, { createContext, useContext, useState } from 'react';

export interface LocationState {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
}

// Sensible default location (New Delhi - prominent urban smog study area)
const DEFAULT_LOCATION: LocationState = {
  city: 'New Delhi',
  country: 'India',
  latitude: 28.6139,
  longitude: 77.2090,
};

interface LocationContextType {
  location: LocationState;
  setLocation: (loc: LocationState) => void;
  requestGPSLocation: () => Promise<void>;
  isLocating: boolean;
  gpsError: string | null;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

export const LocationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [location, setLocationState] = useState<LocationState>(() => {
    try {
      const saved = localStorage.getItem('breathesmart_location');
      return saved ? JSON.parse(saved) : DEFAULT_LOCATION;
    } catch {
      return DEFAULT_LOCATION;
    }
  });
  const [isLocating, setIsLocating] = useState(false);
  const [gpsError, setGpsError] = useState<string | null>(null);

  const setLocation = (loc: LocationState) => {
    setLocationState(loc);
    localStorage.setItem('breathesmart_location', JSON.stringify(loc));
    setGpsError(null);
  };

  const requestGPSLocation = async () => {
    if (!navigator.geolocation) {
      setGpsError('Geolocation is not supported by your browser.');
      return;
    }
    setIsLocating(true);
    setGpsError(null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords = {
          city: 'Your GPS Location',
          country: '',
          latitude: parseFloat(pos.coords.latitude.toFixed(4)),
          longitude: parseFloat(pos.coords.longitude.toFixed(4)),
        };
        setLocation(coords);
        setIsLocating(false);
      },
      () => {
        setGpsError('Location access was denied or timed out. Please enter your city manually.');
        setIsLocating(false);
      },
      { timeout: 10000, enableHighAccuracy: false }
    );
  };

  return (
    <LocationContext.Provider value={{ location, setLocation, requestGPSLocation, isLocating, gpsError }}>
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = () => {
  const ctx = useContext(LocationContext);
  if (!ctx) throw new Error('useLocation must be used within LocationProvider');
  return ctx;
};
