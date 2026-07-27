import React from 'react';
import { Chamber } from '../types';
import { Search, Filter, X } from 'lucide-react';

interface FilterBarProps {
  chamber: Chamber;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedState: string;
  onStateChange: (state: string) => void;
  selectedConstituency: string;
  onConstituencyChange: (c: string) => void;
  statesList: string[];
  constituenciesList: string[];
  onClearFilters: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  chamber,
  searchQuery,
  onSearchChange,
  selectedState,
  onStateChange,
  selectedConstituency,
  onConstituencyChange,
  statesList = [],
  constituenciesList = [],
  onClearFilters
}) => {
  const isHouse = chamber === 'house';
  const labelConstituency = isHouse ? 'Constituency' : 'District';
  const hasActiveFilters = searchQuery !== '' || selectedState !== 'All' || selectedConstituency !== 'All';

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm my-6 space-y-4 md:space-y-0 md:flex md:items-center md:gap-4">
      
      {/* Search Input */}
      <div className="relative flex-1">
        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
          <Search className="w-4 h-4" />
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={e => onSearchChange(e.target.value)}
          placeholder={`Search ${isHouse ? 'Representative' : 'Senator'} by name...`}
          className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 dark:focus:ring-emerald-400/50 transition-all"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Dropdown Filters */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        
        {/* State Filter */}
        <div className="relative w-full sm:w-48">
          <select
            value={selectedState}
            onChange={e => onStateChange(e.target.value)}
            className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-sm font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all appearance-none cursor-pointer"
          >
            <option value="All">All States</option>
            {statesList.map(st => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
            <Filter className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Constituency / District Filter */}
        <div className="relative w-full sm:w-56">
          <select
            value={selectedConstituency}
            onChange={e => onConstituencyChange(e.target.value)}
            className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-sm font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all appearance-none cursor-pointer"
          >
            <option value="All">All {labelConstituency}s</option>
            {constituenciesList.map(c => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
            <Filter className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-all flex items-center justify-center gap-1.5 whitespace-nowrap"
          >
            <X className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        )}

      </div>

    </div>
  );
};
