import { useState, useEffect, useMemo } from 'react';
import { Chamber, ChamberData, Member } from '../types';

export function useData(chamber: Chamber) {
  const [data, setData] = useState<ChamberData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedState, setSelectedState] = useState<string>('All');
  const [selectedConstituency, setSelectedConstituency] = useState<string>('All');

  // Pagination states
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);

  // Fetch JSON data when chamber changes
  useEffect(() => {
    setLoading(true);
    setError(null);
    const jsonPath = chamber === 'house' ? '/data/house.json' : '/data/senate.json';

    fetch(jsonPath)
      .then(res => {
        if (!res.ok) throw new Error(`Failed to load data for ${chamber}`);
        return res.json();
      })
      .then((jsonData: ChamberData) => {
        setData(jsonData);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.message || 'Error loading data');
        setLoading(false);
      });

    // Reset filters when switching chambers
    setSearchQuery('');
    setSelectedState('All');
    setSelectedConstituency('All');
    setCurrentPage(1);
  }, [chamber]);

  // Reset constituency when state changes
  useEffect(() => {
    setSelectedConstituency('All');
    setCurrentPage(1);
  }, [selectedState]);

  // Reset page when search query changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  // Filtered members calculation
  const filteredMembers = useMemo(() => {
    if (!data || !data.members) return [];

    return data.members.filter(m => {
      // 1. Text Search (name or officialName)
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const matchName = m.name.toLowerCase().includes(query);
        const matchOfficial = m.officialName.toLowerCase().includes(query);
        if (!matchName && !matchOfficial) return false;
      }

      // 2. State Filter
      if (selectedState !== 'All' && m.state !== selectedState) {
        return false;
      }

      // 3. Constituency Filter
      if (selectedConstituency !== 'All' && m.constituency !== selectedConstituency) {
        return false;
      }

      return true;
    });
  }, [data, searchQuery, selectedState, selectedConstituency]);

  // Paginated members calculation
  const totalItems = filteredMembers.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  
  const paginatedMembers = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredMembers.slice(start, start + pageSize);
  }, [filteredMembers, currentPage, pageSize]);

  // Available constituencies for selected state
  const availableConstituencies = useMemo(() => {
    if (!data || !data.constituencies) return [];
    if (selectedState === 'All') {
      const all: string[] = [];
      Object.values(data.constituencies).forEach(arr => all.push(...arr));
      return Array.from(new Set(all)).sort();
    }
    return data.constituencies[selectedState] || [];
  }, [data, selectedState]);

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedState('All');
    setSelectedConstituency('All');
    setCurrentPage(1);
  };

  return {
    data,
    loading,
    error,
    searchQuery,
    setSearchQuery,
    selectedState,
    setSelectedState,
    selectedConstituency,
    setSelectedConstituency,
    availableConstituencies,
    filteredMembers,
    paginatedMembers,
    totalItems,
    totalPages,
    currentPage,
    setCurrentPage,
    pageSize,
    setPageSize,
    clearFilters
  };
}
