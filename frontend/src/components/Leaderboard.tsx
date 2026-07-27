import React, { useState } from 'react';
import { LeaderboardEntry, Chamber } from '../types';
import { Trophy, TrendingDown, ChevronDown, ChevronUp, Award } from 'lucide-react';

interface LeaderboardProps {
  chamber: Chamber;
  top20: LeaderboardEntry[];
  least20: LeaderboardEntry[];
}

export const Leaderboard: React.FC<LeaderboardProps> = ({
  chamber,
  top20 = [],
  least20 = []
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<'top' | 'least'>('top');

  const isHouse = chamber === 'house';
  const accentText = isHouse ? 'text-emerald-500' : 'text-rose-500';
  const currentList = activeTab === 'top' ? top20 : least20;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-sm my-8">
      
      {/* Accordion Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 flex items-center justify-between hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-all text-left"
      >
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-2xl ${isHouse ? 'bg-emerald-500/10 text-emerald-600' : 'bg-rose-500/10 text-rose-600'}`}>
            <Trophy className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-extrabold text-slate-900 dark:text-white">
              Legislator Performance Leaderboard
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Rankings based on total bill sponsorship volume in the {isHouse ? 'House of Representatives' : 'Senate'}
            </p>
          </div>
        </div>

        <div className="p-2 rounded-xl text-slate-400">
          {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </div>
      </button>

      {/* Expandable Section */}
      {isOpen && (
        <div className="border-t border-slate-200 dark:border-slate-800 p-6 pt-4 space-y-6">
          
          {/* Toggle Tabs */}
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 p-1.5 rounded-2xl w-fit">
            <button
              onClick={() => setActiveTab('top')}
              className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all flex items-center gap-2 ${
                activeTab === 'top'
                  ? 'bg-amber-500 text-slate-950 shadow-md'
                  : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Trophy className="w-3.5 h-3.5" />
              <span>Top 20 Performers</span>
            </button>
            <button
              onClick={() => setActiveTab('least')}
              className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all flex items-center gap-2 ${
                activeTab === 'least'
                  ? 'bg-slate-800 text-white dark:bg-slate-700 shadow-md'
                  : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <TrendingDown className="w-3.5 h-3.5" />
              <span>Least 20 Performers</span>
            </button>
          </div>

          {/* Leaderboard Table / Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {currentList.map((entry, idx) => {
              const rank = idx + 1;
              const isTop3 = activeTab === 'top' && rank <= 3;

              let rankBadge = (
                <span className="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-extrabold flex items-center justify-center">
                  #{rank}
                </span>
              );

              if (isTop3) {
                if (rank === 1) {
                  rankBadge = (
                    <span className="w-7 h-7 rounded-full bg-gradient-to-br from-amber-300 to-amber-500 text-slate-950 text-xs font-extrabold flex items-center justify-center shadow-md">
                      🥇
                    </span>
                  );
                } else if (rank === 2) {
                  rankBadge = (
                    <span className="w-7 h-7 rounded-full bg-gradient-to-br from-slate-200 to-slate-400 text-slate-950 text-xs font-extrabold flex items-center justify-center shadow-md">
                      🥈
                    </span>
                  );
                } else {
                  rankBadge = (
                    <span className="w-7 h-7 rounded-full bg-gradient-to-br from-amber-600 to-amber-700 text-white text-xs font-extrabold flex items-center justify-center shadow-md">
                      🥉
                    </span>
                  );
                }
              }

              return (
                <div
                  key={entry.id || idx}
                  className="bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-3.5 flex items-center justify-between gap-3 hover:border-slate-300 dark:hover:border-slate-700 transition-all"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    {rankBadge}
                    <div className="min-w-0">
                      <h4 className="font-extrabold text-sm text-slate-900 dark:text-white truncate">
                        {entry.name}
                      </h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                        {entry.state} • {entry.constituency}
                      </p>
                    </div>
                  </div>

                  <div className="text-right flex-shrink-0">
                    <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 inline-block shadow-sm">
                      {entry.billCount} {entry.billCount === 1 ? 'Bill' : 'Bills'}
                    </span>
                    <span className="block text-[10px] text-slate-400 mt-0.5">
                      {entry.sponsoredCount} sponsored
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

        </div>
      )}

    </div>
  );
};
