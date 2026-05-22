export enum GameStatus {
  SCHEDULED = "scheduled",
  LIVE = "live",
  FINISHED = "finished",
  POSTPONED = "postponed"
}

export enum BetType {
  MONEYLINE = "moneyline",
  SPREAD = "spread",
  TOTAL = "total",
  PLAYER_PROPS = "player_props",
  PLAYER_POINTS = "player_points",
  PLAYER_REBOUNDS = "player_rebounds",
  PLAYER_ASSISTS = "player_assists",
  PLAYER_THREES = "player_threes",
  PLAYER_DOUBLE_DOUBLE = "player_double_double",
  PLAYER_TRIPLE_DOUBLE = "player_triple_double",
  TEAM_POINTS = "team_points",
  TEAM_REBOUNDS = "team_rebounds",
  TEAM_ASSISTS = "team_assists"
}

export interface Team {
  id: number;
  name: string;
  abbreviation: string;
  city: string;
  logo_url?: string;
  seed?: number;
}

export interface Odds {
  sportsbook: string;
  bet_type: BetType;
  line?: number;
  odds: number;
  selection: string;
  player_name?: string;
  last_updated: string;
}

export interface BestBet {
  bet_type: BetType;
  selection: string;
  line?: number;
  best_odds: number;
  sportsbook: string;
  player_name?: string;
  confidence: number;
  reasoning: string;
  expected_value: number;
}

export interface Game {
  id: string;
  home_team: Team;
  away_team: Team;
  scheduled_time: string;
  status: GameStatus;
  arena: string;
  series?: string;
  season_type: string;
  odds: Odds[];
}

export interface GameWithBestBets extends Game {
  best_bets: BestBet[];
}