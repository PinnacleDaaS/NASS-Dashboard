import React from 'react';
import { Chamber } from '../types';
import { ExternalLink, Calendar, Code2 } from 'lucide-react';

interface FooterProps {
  chamber: Chamber;
  lastUpdated?: string;
}

export const Footer: React.FC<FooterProps> = ({ chamber, lastUpdated = 'July 27, 2026' }) => {
  const isHouse = chamber === 'house';
  const accentText = isHouse ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400';
  const accentIcon = isHouse ? 'text-emerald-500' : 'text-rose-500';

  return (
    <footer className="border-t border-slate-200 dark:border-slate-800/80 bg-white/90 dark:bg-slate-900/90 glass-panel py-3 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-slate-600 dark:text-slate-400">
        
        {/* Left: Hyperlinked Sources */}
        <div className="flex items-center gap-1.5 font-medium">
          <span>Source:</span>
          <a
            href="https://placbillstrack.org"
            target="_blank"
            rel="noopener noreferrer"
            className={`font-bold ${accentText} hover:underline flex items-center gap-0.5`}
          >
            <span>PLAC</span>
            <ExternalLink className="w-3 h-3" />
          </a>
          <span>|</span>
          <a
            href="https://nass.gov.ng"
            target="_blank"
            rel="noopener noreferrer"
            className={`font-bold ${accentText} hover:underline flex items-center gap-0.5`}
          >
            <span>NASS</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        {/* Middle: Last Updated Date */}
        <div className="flex items-center gap-1.5 font-medium text-slate-500 dark:text-slate-400">
          <Calendar className={`w-3.5 h-3.5 ${accentIcon}`} />
          <span>Last Updated: <strong className="text-slate-800 dark:text-slate-200">{lastUpdated}</strong></span>
        </div>

        {/* Right: Creators Attribution */}
        <div className="flex items-center gap-1.5 font-semibold text-slate-700 dark:text-slate-300">
          <Code2 className={`w-3.5 h-3.5 ${accentIcon}`} />
          <span>Dashboard by</span>
          <strong className="text-slate-900 dark:text-white font-extrabold">
            Joshua Akintayo
          </strong>
          <span>&amp;</span>
          <strong className="text-slate-900 dark:text-white font-extrabold">
            Damilola Aluko
          </strong>
        </div>

      </div>
    </footer>
  );
};
