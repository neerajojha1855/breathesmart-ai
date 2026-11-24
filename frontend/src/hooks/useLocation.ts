import { useContext } from 'react';
import { LocationContext } from '../contexts/locationContextInstance';

export const useLocation = () => {
  const ctx = useContext(LocationContext);
  if (!ctx) throw new Error('useLocation must be used within LocationProvider');
  return ctx;
};
