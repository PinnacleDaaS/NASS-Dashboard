import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { Theme } from '../hooks/useTheme';

interface ThemeToggleProps {
  theme: Theme;
  onToggle: () => void;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ theme, onToggle }) => {
  const isDark = theme === 'dark';

  return (
    <button
      onClick={onToggle}
      aria-label="Toggle Dark and Light Mode"
      className="relative flex items-center bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-full p-1 w-24 h-10 shadow-inner transition-colors duration-300 cursor-pointer focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
    >
      {/* Sliding Pill Background Indicator */}
      <div
        className={`absolute top-1 left-1 w-11 h-8 rounded-full bg-white dark:bg-slate-950 shadow-md transform transition-transform duration-300 ease-in-out ${
          isDark ? 'translate-x-11' : 'translate-x-0'
        }`}
      />

      {/* Light Option Icon & Text */}
      <div
        className={`relative z-10 flex-1 flex items-center justify-center gap-1 text-xs font-bold transition-colors duration-300 ${
          !isDark ? 'text-amber-600 font-extrabold' : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Sun className={`w-3.5 h-3.5 ${!isDark ? 'text-amber-500 fill-amber-400' : 'text-slate-400'}`} />
        <span>Light</span>
      </div>

      {/* Dark Option Icon & Text */}
      <div
        className={`relative z-10 flex-1 flex items-center justify-center gap-1 text-xs font-bold transition-colors duration-300 ${
          isDark ? 'text-indigo-400 font-extrabold' : 'text-slate-500 hover:text-slate-800'
        }`}
      >
        <Moon className={`w-3.5 h-3.5 ${isDark ? 'text-indigo-400 fill-indigo-400' : 'text-slate-500'}`} />
        <span>Dark</span>
      </div>
    </button>
  );
};
