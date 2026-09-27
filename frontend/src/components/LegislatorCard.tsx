import React from 'react';
import { Member, Chamber, isValidParty } from '../types';
import { Avatar } from './Avatar';
import { ConversionGauge } from './ConversionGauge';
import { FileText, Calendar, Eye, MapPin, Award } from 'lucide-react';

interface LegislatorCardProps {
  member: Member;
  chamber: Chamber;
  onViewBills: (member: Member) => void;
  selectedCategory?: string[];
  filteredSponsoredCount?: number;
  filteredCosponsoredCount?: number;
  filteredTotalBills?: number;
}

export const LegislatorCard: React.FC<LegislatorCardProps> = ({
  member,
  chamber,
  onViewBills,
  selectedCategory,
  filteredSponsoredCount,
  filteredCosponsoredCount,
  filteredTotalBills
}) => {
  const isHouse = chamber === 'house';
  const labelConstituency = isHouse ? 'Constituency' : 'District';

  const headerGradient = isHouse
    ? 'bg-gradient-to-r from-emerald-800 via-emerald-700 to-green-600'
    : 'bg-gradient-to-r from-rose-900 via-rose-800 to-red-600';

  const badgeBg = isHouse
    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
    : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20';

  const btnBg = isHouse
    ? 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-900/20'
    : 'bg-rose-600 hover:bg-rose-700 shadow-rose-900/20';

  // Use filtered counts when category is selected, otherwise use member totals
  const isFiltered = selectedCategory && selectedCategory.length > 0 && !selectedCategory.includes('All');
  const displayTotalBills = isFiltered && filteredTotalBills !== undefined ? filteredTotalBills : member.totalBills;
  const displaySponsoredCount = isFiltered && filteredSponsoredCount !== undefined ? filteredSponsoredCount : member.sponsoredCount;
  const displayCosponsoredCount = isFiltered && filteredCosponsoredCount !== undefined ? filteredCosponsoredCount : member.cosponsoredCount;
  const displayTotalBillsForBtn = isFiltered && filteredTotalBills !== undefined ? filteredTotalBills : member.totalBills;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between group">
      
      <div>
        {/* Header Bar */}
        <div className={`p-4 text-white ${headerGradient} relative overflow-hidden`}>
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0 flex-1">
              <h3 className="font-extrabold text-base truncate text-white leading-snug">
                {member.name}
              </h3>
              {isValidParty(member.party) && (
                <p className="text-xs text-white/80 truncate font-semibold uppercase tracking-wider">
                  {member.party}
                </p>
              )}
            </div>

            {/* Total Bills Badge */}
            <span className="px-2.5 py-1 rounded-full text-xs font-extrabold bg-white/20 backdrop-blur-md text-white whitespace-nowrap">
              {displayTotalBills} {displayTotalBills === 1 ? 'Bill' : 'Bills'}
            </span>
          </div>
        </div>

        {/* Body Section */}
        <div className="p-5 space-y-4">
          
          {/* Avatar & Badges Grid */}
          <div className="flex items-center gap-4">
            <Avatar src={member.imageUrl} name={member.name} className="w-16 h-16 flex-shrink-0" />
            
            <div className="flex-1 min-w-0 space-y-1.5">
              {/* State Badge */}
              <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
                <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                <span className="truncate">{member.state || 'N/A'} State</span>
              </div>

              {/* Constituency Badge */}
              <div className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium border ${badgeBg} max-w-full truncate`}>
                <span className="truncate">{member.constituency || 'N/A'}</span>
              </div>

              {/* Party Badge */}
              {isValidParty(member.party) && (
                <div className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 max-w-full truncate">
                  {member.party}
                </div>
              )}
            </div>
          </div>

          {/* Metrics & Conversion Rate */}
          <div className="grid grid-cols-3 gap-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-800">
            
            {/* Sponsored */}
            <div className="text-center">
              <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Sponsored
              </span>
              <span className="text-lg font-extrabold text-slate-900 dark:text-white">
                {displaySponsoredCount}
              </span>
            </div>

            {/* Co-Sponsored */}
            <div className="text-center border-x border-slate-200 dark:border-slate-700/80">
              <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Co-Sponsor
              </span>
              <span className="text-lg font-extrabold text-slate-900 dark:text-white">
                {displayCosponsoredCount}
              </span>
            </div>

            {/* Gauge Column */}
            <div className="flex flex-col items-center justify-center">
              <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">
                3rd Reading
              </span>
              <ConversionGauge rate={member.conversionRate} chamber={chamber} size={36} />
            </div>

          </div>

          {/* Dates Row */}
          {(member.firstBillDate || member.latestBillDate) && (
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 pt-1">
              {member.firstBillDate && (
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  <span>First: <strong className="text-slate-700 dark:text-slate-300">{member.firstBillDate}</strong></span>
                </div>
              )}
              {member.latestBillDate && (
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  <span>Latest: <strong className="text-slate-700 dark:text-slate-300">{member.latestBillDate}</strong></span>
                </div>
              )}
            </div>
          )}

        </div>
      </div>

      {/* Footer Action */}
      <div className="p-4 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/50">
        <button
          onClick={() => onViewBills(member)}
          disabled={displayTotalBillsForBtn === 0}
          className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold text-white transition-all flex items-center justify-center gap-2 shadow-md ${
            displayTotalBillsForBtn > 0
              ? `${btnBg} cursor-pointer`
              : 'bg-slate-300 dark:bg-slate-800 text-slate-500 cursor-not-allowed shadow-none'
          }`}
        >
          <Eye className="w-4 h-4" />
          <span>{displayTotalBillsForBtn > 0 ? 'View Bill Details' : 'No Bills Linked'}</span>
        </button>
      </div>

    </div>
  );
};
