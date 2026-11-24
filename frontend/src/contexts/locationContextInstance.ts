import { createContext } from 'react';
import type { LocationState } from '../types';

export interface LocationContextType {
  location: LocationState;
  setLocation: (loc: LocationState) => void;
  requestGPSLocation: () => Promise<void>;
  isLocating: boolean;
  gpsError: string | null;
}

export const LocationContext = createContext<LocationContextType | undefined>(undefined);
