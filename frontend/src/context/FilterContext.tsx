import React, { createContext, useContext, useState } from 'react';
import type { FilterState } from '../types';

interface FilterContextType {
  filters: FilterState;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  setFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  setScope: (state: string, district?: string, stationId?: string) => void;
  resetFilters: () => void;
}

const defaultFilters: FilterState = {
  state: 'ALL',
  district: 'ALL',
  stationId: 'ALL',
  dateRange: {
    startDate: '2025-01-01',
    endDate: '2025-02-10'
  },
  season: 'ALL',
  rainfallFilter: 'ALL'
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const [searchQuery, setSearchQuery] = useState('');

  const setFilter = <K extends keyof FilterState>(key: K, value: FilterState[K]) => {
    setFilters((prev) => {
      const updated = { ...prev, [key]: value };
      // Cascading reset
      if (key === 'state') {
        updated.district = 'ALL';
        updated.stationId = 'ALL';
      } else if (key === 'district') {
        updated.stationId = 'ALL';
      }
      return updated;
    });
  };

  const setScope = (state: string, district: string = 'ALL', stationId: string = 'ALL') => {
    setFilters((prev) => ({
      ...prev,
      state: state || 'ALL',
      district: district || 'ALL',
      stationId: stationId || 'ALL'
    }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
    setSearchQuery('');
  };

  return (
    <FilterContext.Provider value={{ filters, searchQuery, setSearchQuery, setFilter, setScope, resetFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};
