import React from 'react';
import { Chamber, Stats } from '../types';
import { Users, FileText, Award, Landmark } from 'lucide-react';

interface KPICardsProps {
  chamber: Chamber;
  stats?: Stats;
  filteredCount: number;
  totalLinkedBills: number;
  activeCount: number;
}

export const KPICards: React.FC<KPICardsProps> = ({
  chamber,
  stats,
  filteredCount,
  totalLinkedBills,
  activeCount
}) => {
  const isHouse = chamber === 'house';
  const labelMember = isHouse ? 'Reps' : 'Senators';

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 my-6">
      
      {/* Card 1: Members Shown */}
      <div className={`relative overflow-hidden rounded-2xl p-5 text-white shadow-lg transition-transform duration-200 hover:-translate-y-0.5 ${
        isHouse
          ? 'bg-gradient-to-br from-emerald-800 via-emerald-700 to-green-600 shadow-emerald-950/20'
          : 'bg-gradient-to-br from-rose-950 via-rose-800 to-red-600 shadow-rose-950/20'
      }`}>
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-white/80">
            {labelMember} Shown
          </span>
          <div className="p-2 rounded-xl bg-white/10 backdrop-blur-md">
            <Users className="w-5 h-5 text-white" />
          </div>
        </div>
        <div className="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight">
          {filteredCount}
        </div>
        <div className="mt-1 text-xs text-white/70">
          Filtered in current view
        </div>
      </div>

      {/* Card 2: Linked Bills */}
      <div className={`relative overflow-hidden rounded-2xl p-5 text-white shadow-lg transition-transform duration-200 hover:-translate-y-0.5 ${
        isHouse
          ? 'bg-gradient-to-br from-emerald-900 via-emerald-800 to-green-700 shadow-emerald-950/20'
          : 'bg-gradient-to-br from-red-950 via-rose-900 to-red-700 shadow-rose-950/20'
      }`}>
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-white/80">
            Total Linked Bills
          </span>
          <div className="p-2 rounded-xl bg-white/10 backdrop-blur-md">
            <FileText className="w-5 h-5 text-white" />
          </div>
        </div>
        <div className="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight">
          {totalLinkedBills}
        </div>
        <div className="mt-1 text-xs text-white/70">
          Sponsored & Co-sponsored
        </div>
      </div>

      {/* Card 3: Active Legislators */}
      <div className={`relative overflow-hidden rounded-2xl p-5 text-white shadow-lg transition-transform duration-200 hover:-translate-y-0.5 ${
        isHouse
          ? 'bg-gradient-to-br from-green-900 via-emerald-800 to-teal-700 shadow-emerald-950/20'
          : 'bg-gradient-to-br from-rose-900 via-red-800 to-orange-700 shadow-rose-950/20'
      }`}>
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-white/80">
            Active Legislators
          </span>
          <div className="p-2 rounded-xl bg-white/10 backdrop-blur-md">
            <Award className="w-5 h-5 text-white" />
          </div>
        </div>
        <div className="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight">
          {activeCount}
        </div>
        <div className="mt-1 text-xs text-white/70">
          With ≥ 1 bill sponsored
        </div>
      </div>

      {/* Card 4: Executive Bills */}
      <div className={`relative overflow-hidden rounded-2xl p-5 text-white shadow-lg transition-transform duration-200 hover:-translate-y-0.5 ${
        isHouse
          ? 'bg-gradient-to-br from-emerald-800 via-emerald-700 to-green-600 shadow-emerald-950/20'
          : 'bg-gradient-to-br from-amber-800 via-amber-700 to-yellow-600 shadow-amber-950/20'
      }`}>
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-white/80">
            Executive Bills
          </span>
          <div className="p-2 rounded-xl bg-white/10 backdrop-blur-md">
            <Landmark className="w-5 h-5 text-white" />
          </div>
        </div>
        <div className="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight">
          {stats?.executiveBillCount ?? 0}
        </div>
        <div className="mt-1 text-xs text-white/70">
          Government-sponsored
        </div>
      </div>

    </div>
  );
};
