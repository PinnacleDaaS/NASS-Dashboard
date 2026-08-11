import React, { useState, useMemo } from 'react';
import { Chamber, Member } from './types';
import { useTheme } from './hooks/useTheme';
import { useData } from './hooks/useData';

import { Header } from './components/Header';
import { EmbedToolbar } from './components/EmbedToolbar';
import { Sidebar } from './components/Sidebar';
import { KPICards } from './components/KPICards';
import { Leaderboard } from './components/Leaderboard';
import { ExecutiveBillsAccordion } from './components/ExecutiveBillsAccordion';
import { LegislatorGrid } from './components/LegislatorGrid';
import { Pagination } from './components/Pagination';
import { BillDetailsModal } from './components/BillDetailsModal';
import { Footer } from './components/Footer';

import { RefreshCw, AlertCircle } from 'lucide-react';

export function App() {
  const isEmbed = new URLSearchParams(window.location.search).get('embed') === '1';
  const { theme, toggleTheme } = useTheme();
  const [chamber, setChamber] = useState<Chamber>('house');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);

  const {
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
  } = useData(chamber);

  const [selectedMember, setSelectedMember] = useState<Member | null>(null);

  const isFiltered = searchQuery.trim() !== '' || selectedState !== 'All' || selectedConstituency !== 'All' || selectedCategory !== 'All';

  const totalLinkedBills = filteredMembers.reduce((sum, m) => sum + m.totalBills, 0);
  const activeCount = filteredMembers.filter(m => m.sponsoredCount > 0).length;

  // Dynamic leaderboard from filtered results
  const leaderboardTop20 = useMemo(() => {
    const sorted = [...filteredMembers].sort((a, b) => b.totalBills - a.totalBills);
    return sorted.slice(0, 20).map((m, i) => ({
      id: m.id,
      name: m.name,
      party: m.party,
      state: m.state,
      constituency: m.constituency,
      billCount: m.totalBills,
      sponsoredCount: m.sponsoredCount,
      cosponsoredCount: m.cosponsoredCount,
      conversionRate: 0
    }));
  }, [filteredMembers]);

  const leaderboardLeast20 = useMemo(() => {
    const sorted = [...filteredMembers].sort((a, b) => a.totalBills - b.totalBills);
    return sorted.slice(0, 20).map((m, i) => ({
      id: m.id,
      name: m.name,
      party: m.party,
      state: m.state,
      constituency: m.constituency,
      billCount: m.totalBills,
      sponsoredCount: m.sponsoredCount,
      cosponsoredCount: m.cosponsoredCount,
      conversionRate: 0
    }));
  }, [filteredMembers]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300">
      
      {/* Header with Chamber Switcher & Theme Toggle (full chrome only outside embeds) */}
      {isEmbed ? (
        <EmbedToolbar
          chamber={chamber}
          onChamberChange={setChamber}
          theme={theme}
          onThemeToggle={toggleTheme}
          isSidebarCollapsed={isSidebarCollapsed}
          onToggleSidebar={() => {
            if (window.innerWidth < 1024) {
              setIsMobileSidebarOpen(prev => !prev);
            } else {
              setIsSidebarCollapsed(prev => !prev);
            }
          }}
        />
      ) : (
        <Header
          chamber={chamber}
          onChamberChange={setChamber}
          theme={theme}
          onThemeToggle={toggleTheme}
          isSidebarCollapsed={isSidebarCollapsed}
          onToggleSidebar={() => {
            if (window.innerWidth < 1024) {
              setIsMobileSidebarOpen(prev => !prev);
            } else {
              setIsSidebarCollapsed(prev => !prev);
            }
          }}
        />
      )}

      {/* Main Body Layout (Sidebar + Main Content Area) */}
      <div className="flex-1 flex flex-col lg:flex-row min-w-0">
        
        {/* Collapsible Left Filter Sidebar */}
        <Sidebar
          chamber={chamber}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedState={selectedState}
          onStateChange={setSelectedState}
          selectedConstituency={selectedConstituency}
          onConstituencyChange={setSelectedConstituency}
          statesList={data?.states || []}
          constituenciesList={availableConstituencies}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          categoriesList={availableCategories}
          onClearFilters={clearFilters}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(true)}
          isOpenMobile={isMobileSidebarOpen}
          onCloseMobile={() => setIsMobileSidebarOpen(false)}
        />

        {/* Main Content Dashboard */}
        <div className="flex-1 flex flex-col min-w-0">
          
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            
            {/* Loading State */}
            {loading && (
              <div className="py-24 text-center space-y-4">
                <RefreshCw className="w-10 h-10 mx-auto text-emerald-500 animate-spin" />
                <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">
                  Loading {chamber === 'house' ? 'House of Representatives' : 'Senate'} dataset...
                </p>
              </div>
            )}

            {/* Error State */}
            {error && !loading && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-3xl p-8 text-center my-8 max-w-lg mx-auto space-y-3">
                <AlertCircle className="w-12 h-12 mx-auto text-red-500" />
                <h3 className="text-lg font-bold text-red-600 dark:text-red-400">
                  Data Loading Failed
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {error}
                </p>
              </div>
            )}

            {/* Loaded Content */}
            {!loading && !error && data && (
              <>
                {/* KPI Summary Tile Cards */}
                <KPICards
                  chamber={chamber}
                  stats={data.stats}
                  filteredCount={filteredMembers.length}
                  totalLinkedBills={totalLinkedBills}
                  activeCount={activeCount}
                  isFiltered={isFiltered}
                />

                {/* Performance Leaderboard Section */}
                <Leaderboard
                  chamber={chamber}
                  top20={leaderboardTop20}
                  least20={leaderboardLeast20}
                />

                {/* Government / Executive Bills Section */}
                {!isFiltered && (
                  <ExecutiveBillsAccordion
                    chamber={chamber}
                    bills={data.executiveBills || []}
                  />
                )}

                {/* Pagination Controls Top */}
                <Pagination
                  chamber={chamber}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  pageSize={pageSize}
                  totalItems={totalItems}
                  onPageChange={setCurrentPage}
                  onPageSizeChange={setPageSize}
                />

                {/* Legislators Grid */}
                <LegislatorGrid
                  members={paginatedMembers}
                  chamber={chamber}
                  onViewBills={setSelectedMember}
                  onClearFilters={clearFilters}
                />

                {/* Pagination Controls Bottom */}
                <Pagination
                  chamber={chamber}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  pageSize={pageSize}
                  totalItems={totalItems}
                  onPageChange={setCurrentPage}
                  onPageSizeChange={setPageSize}
                />
              </>
            )}

          </main>

          {/* Slim Single-Line Footer */}
          {!isEmbed && <Footer chamber={chamber} lastUpdated={data?.lastUpdated || 'July 27, 2026'} />}

        </div>

      </div>

      {/* Bill Details Modal */}
      {selectedMember && (
        <BillDetailsModal
          member={selectedMember}
          chamber={chamber}
          onClose={() => setSelectedMember(null)}
        />
      )}

    </div>
  );
}
export default App;
