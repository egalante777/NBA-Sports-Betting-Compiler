from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class GameStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"

class Team(BaseModel):
    id: int
    name: str
    abbreviation: str
    city: str
    logo_url: Optional[str] = None
    seed: Optional[int] = None

class BetType(str, Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    PLAYER_PROPS = "player_props"
    PLAYER_POINTS = "player_points"
    PLAYER_REBOUNDS = "player_rebounds"
    PLAYER_ASSISTS = "player_assists"
    PLAYER_THREES = "player_threes"
    PLAYER_DOUBLE_DOUBLE = "player_double_double"
    PLAYER_TRIPLE_DOUBLE = "player_triple_double"
    TEAM_POINTS = "team_points"
    TEAM_REBOUNDS = "team_rebounds"
    TEAM_ASSISTS = "team_assists"

class Odds(BaseModel):
    sportsbook: str
    bet_type: BetType
    line: Optional[float] = None  # For spread/total
    odds: int  # American odds format
    selection: str  # Which team/over/under/player
    player_name: Optional[str] = None  # For prop bets
    last_updated: datetime

class BestBet(BaseModel):
    bet_type: BetType
    selection: str
    line: Optional[float] = None
    best_odds: int
    sportsbook: str
    player_name: Optional[str] = None  # For prop bets
    confidence: float  # 0-1 confidence score
    reasoning: str
    expected_value: float

class Game(BaseModel):
    id: str
    home_team: Team
    away_team: Team
    scheduled_time: datetime
    status: GameStatus
    arena: str
    series: Optional[str] = None  # e.g., "Eastern Conference Finals Game 1"
    season_type: str = "playoffs"
    odds: List[Odds] = []

class GameWithBestBets(Game):
    best_bets: List[BestBet] = []