export type Chamber = 'house' | 'senate';

export interface Bill {
  billId: string;
  billNumber: string;
  title: string;
  category: string;
  dateFirstReading: string;
  dateSecondReading: string;
  committee: string;
  thirdReadingStatus: string;
  passedThirdReading: boolean;
  primarySponsor: string;
  sponsorsDetails: string;
  pdfInitialBill: string;
  pdfPassedBill: string;
  pdfSignedAct: string;
  pdfCommitteeReport: string;
}

export interface Member {
  id: string;
  name: string;
  officialName: string;
  party: string;
  state: string;
  constituency: string; // Used for constituency (House) or district (Senate)
  imageUrl: string;
  sponsoredBills: Bill[];
  cosponsoredBills: Bill[];
  totalBills: number;
  sponsoredCount: number;
  cosponsoredCount: number;
  conversionRate: number;
  billsPassed: number;
  firstBillDate: string;
  latestBillDate: string;
}

export interface Stats {
  totalMembers: number;
  totalBills: number;
  membersWithBills: number;
  executiveBillCount: number;
}

export interface LeaderboardEntry {
  id: string;
  name: string;
  party: string;
  state: string;
  constituency: string;
  billCount: number;
  sponsoredCount: number;
  cosponsoredCount: number;
  conversionRate: number;
}

export interface ChamberData {
  lastUpdated?: string;
  members: Member[];
  stats: Stats;
  leaderboards: {
    top20: LeaderboardEntry[];
    least20: LeaderboardEntry[];
  };
  executiveBills: Bill[];
  states: string[];
  constituencies: Record<string, string[]>;
}
