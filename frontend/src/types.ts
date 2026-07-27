export type Chamber = 'house' | 'senate';

export interface Bill {
  billId: string;
  title: string;
  dateFirstReading: string;
  dateSecondReading: string;
  committee: string;
  thirdReadingStatus: string;
  passedThirdReading: boolean;
  primarySponsor: string;
  sponsorsDetails: string;
}

export interface Member {
  id: string;
  name: string;
  officialName: string;
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
}

export interface LeaderboardEntry {
  id: string;
  name: string;
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
  states: string[];
  constituencies: Record<string, string[]>;
}
