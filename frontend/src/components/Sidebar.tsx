import React from 'react';
import { Chamber } from '../types';
import { Search, Filter, X, RotateCcw, PanelLeftClose } from 'lucide-react';

interface SidebarProps {
  chamber: Chamber;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedState: string;
  onStateChange: (state: string) => void;
  selectedConstituency: string;
  onConstituencyChange: (c: string) => void;
  selectedCategory: string[];
  onCategoryChange: (c: string[]) => void;
  statesList: string[];
  constituenciesList: string[];
  categoriesList: string[];
  onClearFilters: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  chamber,
  searchQuery,
  onSearchChange,
  selectedState,
  onStateChange,
  selectedConstituency,
  onConstituencyChange,
  selectedCategory,
  onCategoryChange,
  statesList = [],
  constituenciesList = [],
  categoriesList = [],
  onClearFilters,
  isCollapsed,
  onToggleCollapse,
  isOpenMobile,
  onCloseMobile
}) => {
  const isHouse = chamber === 'house';
  const labelConstituency = isHouse ? 'Constituency' : 'District';
  const accentRing = isHouse ? 'focus:ring-emerald-500/50' : 'focus:ring-rose-500/50';
  const accentIcon = isHouse ? 'text-emerald-500' : 'text-rose-500';
  const hasActiveFilters = searchQuery !== '' || selectedState !== 'All' || selectedConstituency !== 'All' || selectedCategory.some(c => c !== 'All');

  const sidebarInner = (
    <div className="flex flex-col h-full space-y-6 p-6">
      
      {/* Sidebar Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <Filter className={`w-4 h-4 ${accentIcon}`} />
          <h2 className="text-sm font-extrabold uppercase tracking-wider text-slate-900 dark:text-white">
            Filter Navigation
          </h2>
        </div>

        {/* Desktop Collapse Close Button */}
        <button
          onClick={onToggleCollapse}
          title="Collapse Sidebar"
          className="hidden lg:flex p-1.5 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
        >
          <PanelLeftClose className="w-4 h-4" />
        </button>

        {/* Mobile Close Button */}
        <button
          onClick={onCloseMobile}
          title="Close Menu"
          className="lg:hidden p-1.5 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* 1. Instant Member Search */}
      <div className="space-y-2">
        <label className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Search Legislator
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={e => onSearchChange(e.target.value)}
            placeholder={`Search ${isHouse ? 'Member' : 'Senator'}...`}
            className={`w-full pl-9 pr-8 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs font-medium text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 ${accentRing} transition-all`}
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute inset-y-0 right-0 pr-2.5 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-white"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* 2. State Filter Dropdown */}
      <div className="space-y-2">
        <label className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Filter by State
        </label>
        <div className="relative">
          <select
            value={selectedState}
            onChange={e => onStateChange(e.target.value)}
            className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 ${accentRing} transition-all appearance-none cursor-pointer"
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
      </div>

      {/* 3. Constituency / District Dropdown */}
      <div className="space-y-2">
        <label className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Filter by {labelConstituency}
        </label>
        <div className="relative">
          <select
            value={selectedConstituency}
            onChange={e => onConstituencyChange(e.target.value)}
            className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 ${accentRing} transition-all appearance-none cursor-pointer"
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
      </div>

{/* 4. Category Filter — Multi-select with Chips */}
      <div className="space-y-2">
        <label className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Filter by Category
        </label>

        {/* Selected Category Chips */}
        {!selectedCategory.includes('All') && selectedCategory.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {selectedCategory.map(cat => (
              <span key={cat} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700/50">
                {cat}
                <button
                  onClick={() => onCategoryChange(selectedCategory.filter(c => c !== cat))}
                  className="p-0.5 rounded-full hover:bg-emerald-200 dark:hover:bg-emerald-700 transition-colors"
                >
                  <X className="w-2.5 h-2.5" />
                </button>
              </span>
            ))}
            <button
              onClick={() => onCategoryChange(['All'])}
              className="inline-flex items-center px-2 py-1 rounded-lg text-[10px] font-bold text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-colors"
            >
              Clear all
            </button>
          </div>
        )}

        {/* Category Dropdown */}
        <div className="relative">
          <select
            value=""
            onChange={e => {
              const cat = e.target.value;
              if (cat && cat !== 'All' && !selectedCategory.includes(cat)) {
                onCategoryChange([...selectedCategory.filter(c => c !== 'All'), cat]);
              } else if (cat === 'All') {
                onCategoryChange(['All']);
              }
            }}
            className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 rounded-xl text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all appearance-none cursor-pointer"
          >
            <option value="" disabled>
              {selectedCategory.includes('All') ? 'Select categories...' : `Add category (${selectedCategory.length} selected)`}
            </option>
            {selectedCategory.includes('All') && (
              <option value="All">All Categories</option>
            )}
            {categoriesList.filter(c => !selectedCategory.includes(c)).map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
            <Filter className="w-3.5 h-3.5" />
          </div>
        </div>
      </div>

      {/* 5. Reset Filters Button */}
      {hasActiveFilters && (
        <button
          onClick={() => {
            onClearFilters();
            onCloseMobile();
          }}
          className="w-full py-2.5 px-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-xs font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all flex items-center justify-center gap-2 cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset All Filters</span>
        </button>
      )}

    </div>
  );

  return (
    <>
      {/* Desktop Collapsible Sidebar */}
      {!isCollapsed && (
        <aside className="hidden lg:block w-72 flex-shrink-0 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto transition-all duration-300">
          {sidebarInner}
        </aside>
      )}

      {/* Mobile Slide-Out Drawer */}
      <div
        className={`lg:hidden fixed inset-0 z-50 flex transition-all duration-300 ease-in-out ${
          isOpenMobile
            ? 'visible opacity-100'
            : 'invisible opacity-0 pointer-events-none'
        }`}
      >
        <div
          className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity duration-300"
          onClick={onCloseMobile}
        />
        <div
          className={`relative w-80 max-w-full bg-white dark:bg-slate-900 h-full shadow-2xl z-10 overflow-y-auto transition-transform duration-300 ease-in-out ${
            isOpenMobile ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          {sidebarInner}
        </div>
      </div>
    </>
  );
};
