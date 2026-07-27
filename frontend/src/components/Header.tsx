import React from 'react';
import { Chamber } from '../types';
import { Theme } from '../hooks/useTheme';
import { Landmark, Building2, Sun, Moon, PanelLeftClose, PanelLeftOpen } from 'lucide-react';

interface HeaderProps {
  chamber: Chamber;
  onChamberChange: (chamber: Chamber) => void;
  theme: Theme;
  onThemeToggle: () => void;
  isSidebarCollapsed: boolean;
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  chamber,
  onChamberChange,
  theme,
  onThemeToggle,
  isSidebarCollapsed,
  onToggleSidebar
}) => {
  const isHouse = chamber === 'house';

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 glass-panel shadow-sm transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Left Section: Sidebar Toggle & Brand */}
        <div className="flex items-center gap-3">
          {/* Sidebar Collapse/Expand Toggle Button */}
          <button
            onClick={onToggleSidebar}
            aria-label="Toggle Filter Sidebar"
            title={isSidebarCollapsed ? 'Expand Filter Sidebar' : 'Collapse Filter Sidebar'}
            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer shadow-sm hover:scale-105"
          >
            {isSidebarCollapsed ? (
              <PanelLeftOpen className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            ) : (
              <PanelLeftClose className="w-5 h-5" />
            )}
          </button>

          {/* Logo & Title */}
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl text-white shadow-md transition-colors duration-300 ${isHouse ? 'bg-emerald-600' : 'bg-rose-600'}`}>
              <Landmark className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
                NASS<span className={isHouse ? 'text-emerald-500' : 'text-rose-500'}>Track</span>
              </h1>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium hidden sm:block">
                10th National Assembly Dashboard
              </p>
            </div>
          </div>
        </div>

        {/* Center: Chamber Switcher Toggle */}
        <div className="bg-slate-100 dark:bg-slate-800/90 p-1.5 rounded-2xl border border-slate-200 dark:border-slate-700/80 flex items-center shadow-inner">
          <button
            onClick={() => onChamberChange('house')}
            className={`flex items-center gap-2 px-3 sm:px-4 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 cursor-pointer ${
              isHouse
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/20'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Building2 className="w-4 h-4" />
            <span className="hidden xs:inline">House of Reps</span>
            <span className="xs:hidden">House</span>
          </button>
          <button
            onClick={() => onChamberChange('senate')}
            className={`flex items-center gap-2 px-3 sm:px-4 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 cursor-pointer ${
              !isHouse
                ? 'bg-rose-600 text-white shadow-md shadow-rose-900/20'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Landmark className="w-4 h-4" />
            <span>Senate</span>
          </button>
        </div>

        {/* Right Section: Single-Icon Theme Toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={onThemeToggle}
            aria-label="Toggle Theme"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer shadow-sm hover:scale-105"
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5 text-amber-400 fill-amber-400" />
            ) : (
              <Moon className="w-5 h-5 text-indigo-600 fill-indigo-600" />
            )}
          </button>
        </div>

      </div>
    </header>
  );
};
