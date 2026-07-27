import React, { useState } from 'react';
import { Bill, Chamber } from '../types';
import { ChevronDown, ChevronUp, FileText, CheckCircle2, Clock, Calendar, Building, ExternalLink, Tag, Landmark } from 'lucide-react';

interface ExecutiveBillsAccordionProps {
  chamber: Chamber;
  bills: Bill[];
}

export const ExecutiveBillsAccordion: React.FC<ExecutiveBillsAccordionProps> = ({
  chamber,
  bills = []
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const isHouse = chamber === 'house';
  const accentBg = isHouse ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400';
  const accentBorder = isHouse ? 'border-emerald-500/20' : 'border-rose-500/20';
  const billBg = isHouse ? 'bg-emerald-50/50 dark:bg-emerald-900/10 border border-emerald-200/70 dark:border-emerald-700/30 hover:border-emerald-300 dark:hover:border-emerald-600/50' : 'bg-amber-50/50 dark:bg-amber-900/10 border border-amber-200/70 dark:border-amber-700/30 hover:border-amber-300 dark:hover:border-amber-600/50';
  const billNumberBg = isHouse ? 'bg-emerald-900 dark:bg-emerald-100 text-white dark:text-emerald-900' : 'bg-amber-900 dark:bg-amber-100 text-white dark:text-amber-900';
  const execBadge = isHouse ? 'bg-emerald-600/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/20' : 'bg-amber-600/10 text-amber-700 dark:text-amber-300 border-amber-500/20';
  const dividerBorder = isHouse ? 'border-emerald-200/60 dark:border-emerald-700/30' : 'border-amber-200/60 dark:border-amber-700/30';

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-sm my-8">
      
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 flex items-center justify-between hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-all text-left"
      >
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-2xl ${accentBg} ${accentBorder}`}>
            <Landmark className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-extrabold text-slate-900 dark:text-white">
              Government / Executive Bills
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {bills.length} bill{bills.length !== 1 ? 's' : ''} sponsored by the Executive branch (Appropriation, Budget, etc.)
            </p>
          </div>
        </div>
        <div className="p-2 rounded-xl text-slate-400">
          {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </div>
      </button>

      {isOpen && (
        <div className="px-6 pb-6 space-y-4">
          {bills.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <Landmark className="w-12 h-12 mx-auto opacity-30 mb-3" />
              <p className="text-sm font-medium">No executive bills found for this chamber.</p>
            </div>
          ) : (
            bills.map((bill, i) => (
              <div
                key={bill.billId || i}
                className={`${billBg} rounded-2xl p-5 transition-all shadow-sm space-y-3`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-3 py-1 rounded-lg text-xs font-mono font-bold ${billNumberBg}`}>
                      {bill.billNumber || `#${i + 1}`}
                    </span>
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold ${execBadge}`}>
                      <Landmark className="w-3 h-3" />
                      Executive
                    </span>
                    {bill.category && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                        <Tag className="w-3 h-3" />
                        {bill.category}
                      </span>
                    )}
                  </div>

                  {bill.passedThirdReading ? (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Third Reading Passed
                    </span>
                  ) : bill.thirdReadingStatus ? (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                      <Clock className="w-3.5 h-3.5" />
                      {bill.thirdReadingStatus}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                      In Progress
                    </span>
                  )}
                </div>

                <h3 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
                  {bill.title}
                </h3>

                <div className={`grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t ${dividerBorder} text-xs text-slate-600 dark:text-slate-400`}>
                  {bill.dateFirstReading && (
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>1st Reading: <strong className="text-slate-800 dark:text-slate-200">{bill.dateFirstReading}</strong></span>
                    </div>
                  )}
                  {bill.dateSecondReading && (
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>2nd Reading: <strong className="text-slate-800 dark:text-slate-200">{bill.dateSecondReading}</strong></span>
                    </div>
                  )}
                  {bill.committee && (
                    <div className="flex items-center gap-1.5 col-span-1 sm:col-span-2">
                      <Building className="w-3.5 h-3.5 text-slate-400" />
                      <span>Committee: <strong className="text-slate-800 dark:text-slate-200">{bill.committee}</strong></span>
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap gap-2 pt-1">
                  {bill.pdfInitialBill && (
                    <a href={bill.pdfInitialBill} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-all">
                      <FileText className="w-3.5 h-3.5" />
                      Initial Bill
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {bill.pdfPassedBill && (
                    <a href={bill.pdfPassedBill} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 hover:bg-blue-500/20 transition-all">
                      <FileText className="w-3.5 h-3.5" />
                      Passed Bill
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {bill.pdfSignedAct && (
                    <a href={bill.pdfSignedAct} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-all">
                      <FileText className="w-3.5 h-3.5" />
                      Signed Act
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {bill.pdfCommitteeReport && (
                    <a href={bill.pdfCommitteeReport} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20 hover:bg-purple-500/20 transition-all">
                      <FileText className="w-3.5 h-3.5" />
                      Committee Report
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

    </div>
  );
};
