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
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  // Pagination states
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(24);

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
    setSelectedCategory('All');
    setCurrentPage(1);
  }, [chamber]);

  // Reset constituency & category when state changes
  useEffect(() => {
    setSelectedConstituency('All');
    setSelectedCategory('All');
    setCurrentPage(1);
  }, [selectedState]);

  // Reset category when constituency changes
  useEffect(() => {
    setSelectedCategory('All');
    setCurrentPage(1);
  }, [selectedConstituency]);

  // Reset page when search query changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

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

  // Members filtered by search + state + constituency (excludes category — used for cascading category options)
  const membersBeforeCategory = useMemo(() => {
    if (!data || !data.members) return [];
    return data.members.filter(m => {
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        if (!m.name.toLowerCase().includes(q) && !m.officialName.toLowerCase().includes(q))
          return false;
      }
      if (selectedState !== 'All' && m.state !== selectedState) return false;
      if (selectedConstituency !== 'All' && m.constituency !== selectedConstituency) return false;
      return true;
    });
  }, [data, searchQuery, selectedState, selectedConstituency]);

  // Available categories — cascades from state/constituency/search
  const availableCategories = useMemo(() => {
    if (!data || !data.members) return [];
    const cats = new Set<string>();
    membersBeforeCategory.forEach(m => {
      [...m.sponsoredBills, ...m.cosponsoredBills].forEach(b => {
        if (b.category) cats.add(b.category);
      });
    });
    return Array.from(cats).sort();
  }, [membersBeforeCategory]);

  // Filtered members — applies all filters including category
  const filteredMembers = useMemo(() => {
    if (selectedCategory === 'All') return membersBeforeCategory;
    return membersBeforeCategory.filter(m => {
      const allBills = [...m.sponsoredBills, ...m.cosponsoredBills];
      return allBills.some(b => b.category === selectedCategory);
    });
  }, [membersBeforeCategory, selectedCategory]);

  // Paginated members calculation
  const totalItems = filteredMembers.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  
  const paginatedMembers = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredMembers.slice(start, start + pageSize);
  }, [filteredMembers, currentPage, pageSize]);

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedState('All');
    setSelectedConstituency('All');
    setSelectedCategory('All');
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
    selectedCategory,
    setSelectedCategory,
    availableCategories,
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
