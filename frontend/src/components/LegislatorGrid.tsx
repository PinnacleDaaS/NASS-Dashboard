import React from 'react';
import { Member, Chamber } from '../types';
import { LegislatorCard } from './LegislatorCard';
import { SearchX } from 'lucide-react';

interface LegislatorGridProps {
  members: Member[];
  chamber: Chamber;
  onViewBills: (m: Member) => void;
  onClearFilters: () => void;
  selectedCategory: string[];
  filteredBillsPerMember: Record<string, string[]>;
}

export const LegislatorGrid: React.FC<LegislatorGridProps> = ({
  members,
  chamber,
  onViewBills,
  onClearFilters,
  selectedCategory,
  filteredBillsPerMember
}) => {
  if (members.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-12 text-center my-8 shadow-sm">
        <SearchX className="w-16 h-16 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">
          No Legislators Found
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-md mx-auto">
          No members matched your search or filter criteria. Try adjusting your search query or selecting a different state/district.
        </p>
        <button
          onClick={onClearFilters}
          className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs font-bold shadow-md hover:opacity-90 transition-all"
        >
          Reset All Filters
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 my-6">
      {members.map(m => {
        const filteredBillIds = filteredBillsPerMember[m.id] || [];
        const isFiltered = selectedCategory.length > 0 && !selectedCategory.includes('All');
        const filteredSponsored = isFiltered
          ? m.sponsoredBills.filter(b => filteredBillIds.includes(b.billId)).length
          : m.sponsoredCount;
        const filteredCosponsored = isFiltered
          ? m.cosponsoredBills.filter(b => filteredBillIds.includes(b.billId)).length
          : m.cosponsoredCount;

        return (
          <LegislatorCard
            key={m.id}
            member={m}
            chamber={chamber}
            onViewBills={onViewBills}
            selectedCategory={selectedCategory}
            filteredSponsoredCount={filteredSponsored}
            filteredCosponsoredCount={filteredCosponsored}
            filteredTotalBills={filteredBillIds.length}
          />
        );
      })}
    </div>
  );
};
