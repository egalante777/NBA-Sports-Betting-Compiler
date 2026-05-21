from fastapi import APIRouter, HTTPException
from typing import List
from ..models.game import Game, GameWithBestBets, Odds, BestBet
from ..services.data_service_factory import DataServiceFactory
from ..services.betting_analyzer import BettingAnalyzer

router = APIRouter(prefix="/api/games", tags=["games"])

# Use factory to get appropriate data service
nba_service = DataServiceFactory.get_nba_service()
betting_analyzer = BettingAnalyzer()

@router.get("/today", response_model=List[Game])
async def get_todays_games():
    """Get today's NBA playoff games"""
    try:
        games = await nba_service.get_todays_games()
        return games
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching games: {str(e)}")

@router.get("/{game_id}/odds", response_model=List[Odds])
async def get_game_odds(game_id: str):
    """Get betting odds for a specific game"""
    try:
        odds = await nba_service.get_game_odds(game_id)
        return odds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching odds: {str(e)}")

@router.get("/{game_id}/best-bets", response_model=List[BestBet])
async def get_best_bets(game_id: str):
    """Get compiled best bets for a specific game"""
    try:
        # Get game details
        games = await nba_service.get_todays_games()
        game = next((g for g in games if g.id == game_id), None)

        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        # Get odds
        odds = await nba_service.get_game_odds(game_id)

        # Analyze and return best bets
        best_bets = betting_analyzer.analyze_best_bets(game, odds)
        return best_bets

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing best bets: {str(e)}")

@router.get("/{game_id}/complete", response_model=GameWithBestBets)
async def get_complete_game_data(game_id: str):
    """Get complete game data including odds and best bets"""
    try:
        # Get game details
        games = await nba_service.get_todays_games()
        game = next((g for g in games if g.id == game_id), None)

        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        # Get odds and best bets
        odds = await nba_service.get_game_odds(game_id)
        best_bets = betting_analyzer.analyze_best_bets(game, odds)

        # Combine into complete response
        game_dict = game.model_dump()
        game_dict["odds"] = odds
        game_dict["best_bets"] = best_bets

        return GameWithBestBets(**game_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching complete game data: {str(e)}")

@router.get("/", response_model=List[GameWithBestBets])
async def get_all_games_with_bets():
    """Get all today's games with their best bets"""
    try:
        games = await nba_service.get_todays_games()
        complete_games = []

        for game in games:
            try:
                # Try to get odds - if API key is missing, continue without odds
                odds = await nba_service.get_game_odds(game.id)
                best_bets = betting_analyzer.analyze_best_bets(game, odds)
            except ValueError as api_key_error:
                if "ODDS_API_KEY" in str(api_key_error):
                    # Graceful degradation: return games without betting analysis
                    odds = []
                    best_bets = []
                else:
                    raise api_key_error

            game_dict = game.model_dump()
            game_dict["odds"] = odds
            game_dict["best_bets"] = best_bets

            complete_games.append(GameWithBestBets(**game_dict))

        return complete_games

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all games data: {str(e)}")

@router.get("/data-source")
async def get_data_source_info():
    """Get information about current NBA data sources"""
    try:
        info = DataServiceFactory.get_service_info()

        # Add real-time API health check if using real data
        if info['data_source'] == 'real':
            try:
                # Try to get today's games as a health check
                games = await nba_service.get_todays_games()
                info['api_health'] = {
                    'status': 'healthy' if games is not None else 'degraded',
                    'games_available': len(games) if games else 0
                }

                # Check odds API specifically
                if not info['odds_api_configured']:
                    info['api_health']['odds_status'] = 'missing_api_key'
                    info['api_health']['message'] = 'Set ODDS_API_KEY environment variable for betting analysis'

            except Exception as health_error:
                info['api_health'] = {
                    'status': 'error',
                    'error': str(health_error)
                }

        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting data source info: {str(e)}")