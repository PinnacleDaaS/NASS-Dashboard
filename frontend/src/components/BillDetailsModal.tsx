import React, { useState } from 'react';
import { Member, Bill, Chamber } from '../types';
import { Avatar } from './Avatar';
import { X, FileText, Calendar, CheckCircle2, Clock, Users, Building, ExternalLink, Tag } from 'lucide-react';

interface BillDetailsModalProps {
  member: Member | null;
  chamber: Chamber;
  onClose: () => void;
}

export const BillDetailsModal: React.FC<BillDetailsModalProps> = ({
  member,
  chamber,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'sponsored' | 'cosponsored'>('sponsored');

  if (!member) return null;

  const isHouse = chamber === 'house';
  const accentBg = isHouse ? 'bg-emerald-600' : 'bg-rose-600';
  const accentText = isHouse ? 'text-emerald-500' : 'text-rose-500';

  const billsToShow: Bill[] = activeTab === 'sponsored' ? member.sponsoredBills : member.cosponsoredBills;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      
      {/* Modal Card */}
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className={`p-6 text-white flex items-start justify-between ${
          isHouse
            ? 'bg-gradient-to-r from-emerald-800 via-emerald-700 to-green-600'
            : 'bg-gradient-to-r from-rose-900 via-rose-800 to-red-600'
        }`}>
          <div className="flex items-start gap-4">
            <Avatar src={member.imageUrl} name={member.name} className="w-14 h-14 flex-shrink-0 border-2 border-white/30" />
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase bg-white/20 backdrop-blur-sm tracking-wider">
                  {member.state} • {member.constituency}
                </span>
                {member.party && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-white/20 backdrop-blur-sm">
                    {member.party}
                  </span>
                )}
              </div>
              <h2 className="text-2xl font-extrabold mt-2 text-white">
                {member.name}
              </h2>
              {member.officialName && (
                <p className="text-xs text-white/80 mt-0.5 font-medium">
                  Official: {member.officialName}
                </p>
              )}
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 px-6">
          <button
            onClick={() => setActiveTab('sponsored')}
            className={`py-3.5 px-4 font-bold text-sm border-b-2 flex items-center gap-2 transition-all ${
              activeTab === 'sponsored'
                ? `${accentText} border-current`
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Sponsored Bills ({member.sponsoredBills.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('cosponsored')}
            className={`py-3.5 px-4 font-bold text-sm border-b-2 flex items-center gap-2 transition-all ${
              activeTab === 'cosponsored'
                ? `${accentText} border-current`
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Co-Sponsored Bills ({member.cosponsoredBills.length})</span>
          </button>
        </div>

        {/* Modal Content / Bill List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {billsToShow.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <FileText className="w-12 h-12 mx-auto opacity-30 mb-3" />
              <p className="text-sm font-medium">
                No {activeTab === 'sponsored' ? 'sponsored' : 'co-sponsored'} bills found for this legislator.
              </p>
            </div>
          ) : (
            billsToShow.map((bill, i) => (
              <div
                key={bill.billId || i}
                className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/70 rounded-2xl p-5 hover:border-slate-300 dark:hover:border-slate-600 transition-all shadow-sm space-y-3"
              >
                {/* Header: Bill Number, Category & Status Badge */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-3 py-1 rounded-lg text-xs font-mono font-bold bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900">
                      {bill.billNumber || `#${i + 1}`}
                    </span>
                    {bill.category && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                        <Tag className="w-3 h-3" />
                        {bill.category}
                      </span>
                    )}
                  </div>

                  {/* Third Reading Badge */}
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

                {/* Bill Title */}
                <h3 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
                  {bill.title}
                </h3>

                {/* Details Meta Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-slate-200/60 dark:border-slate-700/60 text-xs text-slate-600 dark:text-slate-400">
                  
                  {/* First Reading */}
                  {bill.dateFirstReading && (
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>1st Reading: <strong className="text-slate-800 dark:text-slate-200">{bill.dateFirstReading}</strong></span>
                    </div>
                  )}

                  {/* Second Reading */}
                  {bill.dateSecondReading && (
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>2nd Reading: <strong className="text-slate-800 dark:text-slate-200">{bill.dateSecondReading}</strong></span>
                    </div>
                  )}

                  {/* Committee */}
                  {bill.committee && (
                    <div className="flex items-center gap-1.5 col-span-1 sm:col-span-2">
                      <Building className="w-3.5 h-3.5 text-slate-400" />
                      <span>Committee: <strong className="text-slate-800 dark:text-slate-200">{bill.committee}</strong></span>
                    </div>
                  )}

                  {/* Primary Sponsor text if co-sponsored */}
                  {activeTab === 'cosponsored' && bill.primarySponsor && (
                    <div className="flex items-center gap-1.5 col-span-1 sm:col-span-2 text-xs">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      <span>Primary Sponsor: <strong className="text-slate-800 dark:text-slate-200">{bill.primarySponsor}</strong></span>
                    </div>
                  )}
                </div>

                {/* PDF Links */}
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

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex justify-end">
          <button
            onClick={onClose}
            className={`px-5 py-2.5 rounded-xl font-bold text-xs text-white ${accentBg} hover:opacity-90 transition-all shadow-md`}
          >
            Close Window
          </button>
        </div>

      </div>
    </div>
  );
};
