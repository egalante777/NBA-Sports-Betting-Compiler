import httpx
import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from ..models.game import Game, Team, GameStatus, Odds, BetType
import os
import json

class RealNBAService:
    """
    Real NBA data service using multiple APIs for live game data and odds.

    APIs Used:
    1. NBA Stats API (Official) - Game schedules and team data
    2. ESPN API - Game information and status
    3. The Odds API - Live betting odds (requires API key)
    4. balldontlie API - Fallback for team/game data
    """

    def __init__(self):
        # Official NBA APIs
        self.nba_stats_base = "https://stats.nba.com/stats"
        self.nba_api_base = "https://stats.nba.com/stats"  # Alias for test compatibility
        self.nba_data_base = "https://data.nba.net/10s/prod/v1"

        # ESPN API
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"

        # Odds API (premium)
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.odds_api_base = "https://api.the-odds-api.com/v4"

        # Free alternative APIs
        self.balldontlie_base = "https://www.balldontlie.io/api/v1"

        # HTTP client with proper headers
        self.headers = {
            'User-Agent': 'NBA-Betting-Compiler/1.0 (https://github.com/user/nba-betting-compiler)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        }

        # API call caching to conserve credits (cache for 5 minutes)
        self._odds_cache = {}
        self._games_cache = {}
        self._cache_duration = 300  # 5 minutes

    async def get_todays_games(self) -> List[Game]:
        """Fetch today's NBA games from multiple sources"""

        # Check if development playoff mode is enabled
        if os.getenv("ENABLE_DEV_PLAYOFF_MODE") == "true":
            print("🏀 Development playoff mode enabled - showing Knicks vs Cavaliers Game 7")
            return await self._get_dev_playoff_games()

        try:
            # Try ESPN API first (most reliable for current games)
            games = await self._fetch_espn_games()

            if not games:
                # Fallback to NBA Data API
                games = await self._fetch_nba_data_games()

            if not games:
                # Final fallback to balldontlie
                games = await self._fetch_balldontlie_games()

            return games

        except Exception as e:
            print(f"Error fetching real NBA games: {e}")
            return []

    async def _fetch_espn_games(self) -> List[Game]:
        """Fetch games from ESPN API - looks for today's games, then upcoming games"""
        try:
            # Try today first
            games = await self._fetch_espn_games_for_date(date.today())

            # If no games today, look for upcoming games in the next 3 days
            if not games:
                print("No games today, looking for upcoming games...")
                for days_ahead in range(1, 4):
                    future_date = date.today() + timedelta(days=days_ahead)
                    games = await self._fetch_espn_games_for_date(future_date)
                    if games:
                        print(f"Found {len(games)} upcoming games on {future_date}")
                        break

            return games

        except Exception as e:
            print(f"ESPN API error: {e}")
            return []

    async def _fetch_espn_games_for_date(self, target_date: date) -> List[Game]:
        """Fetch ESPN games for a specific date"""
        try:
            date_str = target_date.strftime("%Y%m%d")
            url = f"{self.espn_base}/scoreboard"

            # Add date parameter if not today
            params = {}
            if target_date != date.today():
                params['dates'] = date_str

            async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    return []

                data = response.json()
                games = []

                print(f"ESPN API returned {len(data.get('events', []))} events for {target_date}")

                for event in data.get('events', []):
                    # Include playoff/postseason games (regular season = 2, playoffs = 3)
                    season_type = event.get('season', {})
                    season_slug = season_type.get('slug', '')
                    season_type_id = season_type.get('type', 0)

                    # Accept playoffs (type 3) or postseason games
                    if season_type_id != 3 and 'post' not in season_slug.lower():
                        print(f"Skipping non-playoff game: {season_slug} (type {season_type_id})")
                        continue

                    print(f"Processing playoff game: {season_slug} (type {season_type_id})")
                    game = await self._parse_espn_game(event)
                    if game:
                        games.append(game)

                return games

        except Exception as e:
            print(f"ESPN API error for {target_date}: {e}")
            return []


    async def _parse_espn_game(self, event_data: Dict) -> Optional[Game]:
        """Parse ESPN game data into our Game model"""
        try:
            # Extract basic game info
            game_id = f"nba_{event_data['date'][:10]}_{event_data['id']}"

            # Get teams
            competitors = event_data.get('competitions', [{}])[0].get('competitors', [])
            if len(competitors) != 2:
                return None

            home_team = None
            away_team = None

            for comp in competitors:
                team_data = comp.get('team', {})
                is_home = comp.get('homeAway') == 'home'

                team = Team(
                    id=int(team_data.get('id', 0)),
                    name=team_data.get('displayName', ''),
                    abbreviation=team_data.get('abbreviation', ''),
                    city=team_data.get('location', ''),
                    logo_url=team_data.get('logo', '')
                )

                if is_home:
                    home_team = team
                else:
                    away_team = team

            if not home_team or not away_team:
                return None

            # Parse game status
            status_type = event_data.get('status', {}).get('type', {}).get('name', '')
            if status_type == 'STATUS_SCHEDULED':
                status = GameStatus.SCHEDULED
            elif status_type in ['STATUS_IN_PROGRESS', 'STATUS_HALFTIME']:
                status = GameStatus.LIVE
            elif status_type == 'STATUS_FINAL':
                status = GameStatus.FINISHED
            else:
                status = GameStatus.SCHEDULED

            # Parse venue and series info
            venue = event_data.get('competitions', [{}])[0].get('venue', {})
            arena = venue.get('fullName', 'Unknown Arena')

            # Series information (if available)
            series_info = event_data.get('competitions', [{}])[0].get('notes', [])
            series = None
            for note in series_info:
                if 'series' in note.get('headline', '').lower():
                    series = note.get('headline', '')
                    break

            # Scheduled time
            scheduled_time = datetime.fromisoformat(event_data['date'].replace('Z', '+00:00'))

            return Game(
                id=game_id,
                home_team=home_team,
                away_team=away_team,
                scheduled_time=scheduled_time.isoformat(),
                status=status,
                arena=arena,
                series=series,
                season_type="playoffs",
                odds=[]
            )

        except Exception as e:
            print(f"Error parsing ESPN game: {e}")
            return None

    async def _fetch_nba_data_games(self) -> List[Game]:
        """Fetch from official NBA data API"""
        try:
            today = date.today().strftime("%Y%m%d")
            url = f"{self.nba_data_base}/{today}/scoreboard.json"

            async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()
                    # Parse NBA official data format
                    return await self._parse_nba_official_data(data)

        except Exception as e:
            print(f"NBA Data API error: {e}")

        return []

    async def _fetch_balldontlie_games(self) -> List[Game]:
        """Fetch from balldontlie free API"""
        try:
            today = date.today().strftime("%Y-%m-%d")
            url = f"{self.balldontlie_base}/games"
            params = {
                'dates[]': today,
                'seasons[]': '2025',  # Current season
                'postseason': 'true'
            }

            async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return await self._parse_balldontlie_data(data)

        except Exception as e:
            print(f"balldontlie API error: {e}")

        return []

    async def get_real_odds(self, game_id: str) -> List[Odds]:
        """Fetch real betting odds from The Odds API - REQUIRES API KEY"""
        if not self.odds_api_key:
            raise ValueError(
                "ODDS_API_KEY environment variable is required for betting odds. "
                "Sign up at https://the-odds-api.com/ to get your API key."
            )

        # Check cache first to avoid unnecessary API calls
        cache_key = f"odds_{game_id}_{datetime.now().strftime('%Y%m%d_%H%M')}"  # Cache by game and 5-min intervals
        current_time = datetime.now().timestamp()

        if cache_key in self._odds_cache:
            cache_entry = self._odds_cache[cache_key]
            if current_time - cache_entry['timestamp'] < self._cache_duration:
                print(f"💾 Using cached odds data (saving API credits)")
                return cache_entry['data']

        try:
            url = f"{self.odds_api_base}/sports/basketball_nba/odds"
            # Default to basic markets to conserve API credits
            # Enable prop bets via environment variable: ENABLE_PROP_BETS=true
            base_markets = 'h2h,spreads,totals'
            # Using correct Odds API market names for NBA props
            prop_markets = 'player_points_over_under,player_rebounds_over_under,player_assists_over_under'

            markets = base_markets
            if os.getenv("ENABLE_PROP_BETS", "false").lower() == "true":
                markets += f",{prop_markets}"
                print(f"🎯 Prop bets enabled - requesting {len(markets.split(','))} markets")
            else:
                print(f"💰 API credit conservation mode - requesting only {len(base_markets.split(','))} basic markets")

            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us',
                'markets': markets,
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    odds_data = response.json()
                    parsed_odds = await self._parse_odds_data(odds_data, game_id)

                    # Cache the result to save future API calls
                    self._odds_cache[cache_key] = {
                        'data': parsed_odds,
                        'timestamp': current_time
                    }
                    print(f"💾 Cached odds data for future requests")

                    return parsed_odds
                elif response.status_code == 401:
                    raise ValueError("Invalid ODDS_API_KEY. Please check your API key.")
                elif response.status_code == 402:
                    raise ValueError("Odds API quota exceeded. Please upgrade your plan.")
                else:
                    raise Exception(f"Odds API returned status {response.status_code}")

        except ValueError:
            # Re-raise configuration errors
            raise
        except Exception as e:
            raise Exception(f"Error fetching betting odds: {e}")

        return []

    async def _parse_odds_data(self, odds_data: List[Dict], target_game_id: str) -> List[Odds]:
        """Parse odds data from The Odds API"""
        odds_list = []

        try:
            # First, get the target game info from our internal game ID
            target_game = None
            games = await self.get_todays_games()
            for game in games:
                if game.id == target_game_id:
                    target_game = game
                    break

            if not target_game:
                print(f"Could not find target game {target_game_id}")
                return []

            for game_odds in odds_data:
                # Match game by teams (since IDs may differ between APIs)
                api_home_team = game_odds.get('home_team', '')
                api_away_team = game_odds.get('away_team', '')

                # Check if this odds data matches our target game
                target_home_name = target_game.home_team.name
                target_away_name = target_game.away_team.name

                # Fuzzy matching - check if team names are contained in each other
                home_match = (
                    target_home_name.lower() in api_home_team.lower() or
                    api_home_team.lower() in target_home_name.lower() or
                    target_game.home_team.abbreviation.lower() in api_home_team.lower()
                )
                away_match = (
                    target_away_name.lower() in api_away_team.lower() or
                    api_away_team.lower() in target_away_name.lower() or
                    target_game.away_team.abbreviation.lower() in api_away_team.lower()
                )

                # Only process odds for the matching game
                if not (home_match and away_match):
                    print(f"Skipping odds for {api_home_team} vs {api_away_team} (target: {target_home_name} vs {target_away_name})")
                    continue

                print(f"Processing odds for matching game: {api_home_team} vs {api_away_team}")

                # Parse bookmaker odds
                for bookmaker in game_odds.get('bookmakers', []):
                    sportsbook = bookmaker.get('title', 'Unknown')

                    for market in bookmaker.get('markets', []):
                        market_key = market.get('key', '')

                        # Parse different bet types
                        if market_key == 'h2h':  # Moneyline
                            for outcome in market.get('outcomes', []):
                                odds_list.append(Odds(
                                    sportsbook=sportsbook,
                                    bet_type=BetType.MONEYLINE,
                                    odds=int(outcome.get('price', 0)),
                                    selection=outcome.get('name', ''),
                                    last_updated=datetime.now().isoformat()
                                ))

                        elif market_key == 'spreads':  # Point spread
                            for outcome in market.get('outcomes', []):
                                odds_list.append(Odds(
                                    sportsbook=sportsbook,
                                    bet_type=BetType.SPREAD,
                                    line=float(outcome.get('point', 0)),
                                    odds=int(outcome.get('price', 0)),
                                    selection=outcome.get('name', ''),
                                    last_updated=datetime.now().isoformat()
                                ))

                        elif market_key == 'totals':  # Over/Under
                            for outcome in market.get('outcomes', []):
                                odds_list.append(Odds(
                                    sportsbook=sportsbook,
                                    bet_type=BetType.TOTAL,
                                    line=float(outcome.get('point', 0)),
                                    odds=int(outcome.get('price', 0)),
                                    selection=outcome.get('name', '').lower(),
                                    last_updated=datetime.now().isoformat()
                                ))

                        # Player prop bets (using correct API market names)
                        elif market_key in ['player_points_over_under', 'player_rebounds_over_under', 'player_assists_over_under']:
                            for outcome in market.get('outcomes', []):
                                # Parse player name from description
                                description = outcome.get('description', '')
                                player_name = self._extract_player_name(description)

                                bet_type_map = {
                                    'player_points_over_under': BetType.PLAYER_POINTS,
                                    'player_rebounds_over_under': BetType.PLAYER_REBOUNDS,
                                    'player_assists_over_under': BetType.PLAYER_ASSISTS
                                }

                                odds_list.append(Odds(
                                    sportsbook=sportsbook,
                                    bet_type=bet_type_map[market_key],
                                    line=float(outcome.get('point', 0)),
                                    odds=int(outcome.get('price', 0)),
                                    selection=outcome.get('name', '').lower(),  # over/under
                                    player_name=player_name,
                                    last_updated=datetime.now().isoformat()
                                ))

                        # Special player achievement props
                        elif market_key in ['player_double_double', 'player_triple_double']:
                            for outcome in market.get('outcomes', []):
                                description = outcome.get('description', '')
                                player_name = self._extract_player_name(description)

                                bet_type_map = {
                                    'player_double_double': BetType.PLAYER_DOUBLE_DOUBLE,
                                    'player_triple_double': BetType.PLAYER_TRIPLE_DOUBLE
                                }

                                odds_list.append(Odds(
                                    sportsbook=sportsbook,
                                    bet_type=bet_type_map[market_key],
                                    odds=int(outcome.get('price', 0)),
                                    selection=outcome.get('name', '').lower(),  # yes/no
                                    player_name=player_name,
                                    last_updated=datetime.now().isoformat()
                                ))

                        # Team prop bets
                        elif market_key in ['team_points', 'team_rebounds', 'team_assists']:
                            for outcome in market.get('outcomes', []):
                                bet_type_map = {
                                    'team_points': BetType.TEAM_POINTS,
                                    'team_rebounds': BetType.TEAM_REBOUNDS,
                                    'team_assists': BetType.TEAM_ASSISTS
                                }

                                odds_list.append(Odds(
                                    sportsbook=sportsbook,
                                    bet_type=bet_type_map[market_key],
                                    line=float(outcome.get('point', 0)),
                                    odds=int(outcome.get('price', 0)),
                                    selection=outcome.get('name', ''),  # team name + over/under
                                    last_updated=datetime.now().isoformat()
                                ))

        except Exception as e:
            print(f"Error parsing odds data: {e}")

        return odds_list

    def _extract_player_name(self, description: str) -> str:
        """Extract player name from prop bet description"""
        # The Odds API typically formats player props like:
        # "Jalen Brunson Over 24.5 Points" or "Donovan Mitchell Under 5.5 Rebounds"
        if not description:
            return "Unknown Player"

        # Remove common prop bet terms to isolate the player name
        cleaned = description
        for term in [' Over ', ' Under ', ' Points', ' Rebounds', ' Assists', ' Threes', ' Double Double', ' Triple Double']:
            cleaned = cleaned.replace(term, '')

        # Split by numbers and take the first part (should be player name)
        parts = cleaned.split()
        player_parts = []
        for part in parts:
            # Stop when we hit a number
            if any(char.isdigit() for char in part):
                break
            player_parts.append(part)

        return ' '.join(player_parts).strip() if player_parts else "Unknown Player"

    async def check_api_health(self) -> Dict[str, bool]:
        """Check which APIs are available"""
        health = {}

        # Test ESPN API
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.espn_base}/scoreboard")
                health['espn'] = response.status_code == 200
        except:
            health['espn'] = False

        # Test Odds API (if key available)
        if self.odds_api_key:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        f"{self.odds_api_base}/sports/basketball_nba/odds",
                        params={'apiKey': self.odds_api_key}
                    )
                    health['odds_api'] = response.status_code == 200
            except:
                health['odds_api'] = False
        else:
            health['odds_api'] = False

        # Test balldontlie
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.balldontlie_base}/games")
                health['balldontlie'] = response.status_code == 200
        except:
            health['balldontlie'] = False

        return health


    async def get_game_odds(self, game_id: str) -> List[Odds]:
        """Get betting odds for a specific game (wrapper for compatibility)"""
        return await self.get_real_odds(game_id)

    async def _get_dev_playoff_games(self) -> List[Game]:
        """Return mock playoff game for development - Knicks vs Cavaliers Eastern Conference Finals Game 2"""
        from datetime import datetime, timedelta

        # Create the expected playoff game for tonight
        tonight = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)

        return [Game(
            id="nba_2026-05-21_401873342",
            home_team=Team(
                id=18,
                name="Knicks",
                abbreviation="NYK",
                city="New York",
                seed=2
            ),
            away_team=Team(
                id=5,
                name="Cavaliers",
                abbreviation="CLE",
                city="Cleveland",
                seed=4
            ),
            scheduled_time=tonight.isoformat(),
            status=GameStatus.SCHEDULED,
            arena="Madison Square Garden",
            series="Eastern Conference Finals - Game 2",
            season_type="playoffs",
            odds=[]
        )]