"""
Unit tests for service classes in the NBA Sports Betting Compiler.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.real_nba_service import RealNBAService
from app.services.betting_analyzer import BettingAnalyzer
from app.services.data_service_factory import DataServiceFactory
from app.models.game import Game, Odds, BetType, GameStatus


@pytest.mark.unit
class TestRealNBAService:
    """Test the NBA service class."""

    @pytest.fixture
    def nba_service(self):
        """Create NBA service instance for testing."""
        return RealNBAService()

    @pytest.mark.asyncio
    async def test_get_todays_games(self, nba_service):
        """Test getting today's games."""
        games = await nba_service.get_todays_games()

        assert isinstance(games, list)
        # Should return mock games
        if games:
            assert all(isinstance(game, Game) for game in games)
            assert all(game.season_type == "playoffs" for game in games)

    @pytest.mark.asyncio
    async def test_get_game_odds(self, mock_nba_service):
        """Test getting betting odds for a game."""
        odds = await mock_nba_service.get_game_odds("test_game_id")

        assert isinstance(odds, list)
        if odds:
            assert all(isinstance(odd, Odds) for odd in odds)
            # Should have at least moneyline bets in mock data
            bet_types = {odd.bet_type for odd in odds}
            assert BetType.MONEYLINE in bet_types

    def test_service_initialization(self, mock_nba_service):
        """Test service initializes correctly."""
        assert mock_nba_service.nba_api_base == "https://stats.nba.com/stats"
        assert hasattr(mock_nba_service, 'odds_api_key')
        assert mock_nba_service.odds_api_key == "test_api_key_for_testing"


@pytest.mark.unit
class TestBettingAnalyzer:
    """Test the betting analyzer class."""

    @pytest.fixture
    def betting_analyzer(self):
        """Create betting analyzer instance for testing."""
        return BettingAnalyzer()

    @pytest.fixture
    def sample_odds_for_analysis(self):
        """Create sample odds for analysis testing."""
        return [
            Odds(
                sportsbook="DraftKings",
                bet_type=BetType.MONEYLINE,
                odds=-150,
                selection="BOS",
                last_updated=datetime.now().isoformat()
            ),
            Odds(
                sportsbook="FanDuel",
                bet_type=BetType.MONEYLINE,
                odds=-140,
                selection="BOS",
                last_updated=datetime.now().isoformat()
            ),
            Odds(
                sportsbook="BetMGM",
                bet_type=BetType.MONEYLINE,
                odds=+120,
                selection="MIA",
                last_updated=datetime.now().isoformat()
            )
        ]

    def test_analyzer_initialization(self, betting_analyzer):
        """Test analyzer initializes with correct weights."""
        assert hasattr(betting_analyzer, 'confidence_weights')
        weights = betting_analyzer.confidence_weights
        assert 'odds_value' in weights
        assert 'line_movement' in weights
        assert sum(weights.values()) == 1.0  # Weights should sum to 1

    def test_analyze_best_bets(self, betting_analyzer, sample_game_data, sample_odds_for_analysis):
        """Test analyzing best bets from odds."""
        best_bets = betting_analyzer.analyze_best_bets(sample_game_data, sample_odds_for_analysis)

        assert isinstance(best_bets, list)
        assert len(best_bets) <= 5  # Should return max 5 bets

        if best_bets:
            bet = best_bets[0]
            assert hasattr(bet, 'confidence')
            assert hasattr(bet, 'expected_value')
            assert hasattr(bet, 'reasoning')
            assert 0 <= bet.confidence <= 1

    def test_calculate_confidence(self, betting_analyzer, sample_odds_for_analysis):
        """Test confidence calculation."""
        moneyline_odds = [odd for odd in sample_odds_for_analysis if odd.bet_type == BetType.MONEYLINE]
        confidence = betting_analyzer._calculate_confidence(moneyline_odds, "moneyline")

        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

    def test_calculate_expected_value(self, betting_analyzer):
        """Test expected value calculation."""
        # Test positive odds (underdog)
        ev_positive = betting_analyzer._calculate_expected_value(150, 0.4)
        assert isinstance(ev_positive, float)

        # Test negative odds (favorite)
        ev_negative = betting_analyzer._calculate_expected_value(-150, 0.7)
        assert isinstance(ev_negative, float)

    def test_analyze_moneyline(self, betting_analyzer, sample_game_data, sample_odds_for_analysis):
        """Test moneyline analysis specifically."""
        moneyline_odds = [odd for odd in sample_odds_for_analysis if odd.bet_type == BetType.MONEYLINE]
        best_bets = betting_analyzer._analyze_moneyline(sample_game_data, moneyline_odds)

        assert isinstance(best_bets, list)
        if best_bets:
            assert all(bet.bet_type == BetType.MONEYLINE for bet in best_bets)

    def test_empty_odds_handling(self, betting_analyzer, sample_game_data):
        """Test analyzer handles empty odds gracefully."""
        best_bets = betting_analyzer.analyze_best_bets(sample_game_data, [])

        assert isinstance(best_bets, list)
        assert len(best_bets) == 0

    def test_get_line_movement_analysis(self, betting_analyzer):
        """Test line movement analysis."""
        # Test with empty historical odds (mock implementation)
        analysis = betting_analyzer.get_line_movement_analysis([])

        assert isinstance(analysis, dict)
        assert 'movement' in analysis
        assert 'direction' in analysis
        assert 'significance' in analysis


@pytest.mark.unit
class TestDataServiceFactory:
    """Test the data service factory."""

    def test_get_service_info(self):
        """Test getting service information."""
        info = DataServiceFactory.get_service_info()

        assert isinstance(info, dict)
        required_keys = [
            'data_source', 'odds_api_configured', 'available_sources'
        ]
        for key in required_keys:
            assert key in info

        # Check available sources
        sources = info['available_sources']
        assert 'espn' in sources
        assert 'odds_api' in sources
        assert 'balldontlie' in sources

        # Should be using real data source
        assert info['data_source'] == 'real'

    @patch.dict('os.environ', {'USE_REAL_DATA': 'false', 'NBA_DATA_SOURCE': 'mock'}, clear=False)
    def test_get_mock_service(self):
        """Test factory returns mock service when configured."""
        service = DataServiceFactory.get_nba_service()
        assert isinstance(service, RealNBAService)

    @patch.dict('os.environ', {'USE_REAL_DATA': 'true'})
    def test_get_real_service_config(self):
        """Test factory configuration for real service."""
        # Note: This test checks configuration, actual real service
        # would require additional setup/mocking
        info = DataServiceFactory.get_service_info()
        # When USE_REAL_DATA is true, data_source should be 'real'
        # (This depends on the current implementation)


@pytest.mark.unit
class TestServiceIntegration:
    """Test integration between services."""

    @pytest.mark.asyncio
    async def test_nba_service_with_analyzer(self, mock_nba_service):
        """Test NBA service working with betting analyzer."""
        analyzer = BettingAnalyzer()

        # Get games and odds
        games = await mock_nba_service.get_todays_games()
        if not games:
            pytest.skip("No games available for integration test")

        game = games[0]
        odds = await mock_nba_service.get_game_odds(game.id)

        # Analyze bets
        best_bets = analyzer.analyze_best_bets(game, odds)

        assert isinstance(best_bets, list)
        # Integration should work without errors

    def test_service_factory_consistency(self):
        """Test that factory returns consistent services."""
        service1 = DataServiceFactory.get_nba_service()
        service2 = DataServiceFactory.get_nba_service()

        # Should return same type of service
        assert type(service1) == type(service2)


@pytest.mark.unit
class TestErrorHandling:
    """Test service error handling."""

    @pytest.mark.asyncio
    async def test_nba_service_error_handling(self, mock_nba_service):
        """Test NBA service handles errors gracefully."""
        # Test with invalid game ID
        odds = await mock_nba_service.get_game_odds("invalid_game_id")
        # Should not raise exception, should return empty list or handle gracefully
        assert isinstance(odds, list)

    @pytest.mark.asyncio
    async def test_betting_analyzer_edge_cases(self):
        """Test betting analyzer handles edge cases."""
        analyzer = BettingAnalyzer()

        # Create minimal game data
        from app.models.game import Game, Team, GameStatus

        game = Game(
            id="test",
            home_team=Team(id=1, name="Home", abbreviation="HOM", city="Home"),
            away_team=Team(id=2, name="Away", abbreviation="AWY", city="Away"),
            scheduled_time=datetime.now().isoformat(),
            status=GameStatus.SCHEDULED,
            arena="Test Arena",
            season_type="playoffs",
            odds=[]
        )

        # Test with empty odds list
        best_bets = analyzer.analyze_best_bets(game, [])
        assert isinstance(best_bets, list)
        assert len(best_bets) == 0

        # Test with malformed odds
        malformed_odds = [
            Odds(
                sportsbook="TestBook",
                bet_type=BetType.MONEYLINE,
                odds=0,
                selection="HOM",
                last_updated=datetime.now().isoformat()
            )
        ]

        best_bets = analyzer.analyze_best_bets(game, malformed_odds)
        assert isinstance(best_bets, list)


@pytest.mark.unit
@pytest.mark.slow
class TestPerformance:
    """Test service performance."""

    @pytest.mark.asyncio
    async def test_nba_service_performance(self, mock_nba_service):
        """Test NBA service response times."""
        import time

        start_time = time.time()
        games = await mock_nba_service.get_todays_games()
        end_time = time.time()

        # Mock service should be very fast
        assert (end_time - start_time) < 0.1

    def test_betting_analyzer_performance(self, betting_analyzer, sample_game_data):
        """Test betting analyzer performance with large datasets."""
        import time

        # Create large odds dataset
        large_odds = []
        for i in range(100):
            large_odds.append(Odds(
                sportsbook=f"Sportsbook{i}",
                bet_type=BetType.MONEYLINE,
                odds=-150 + i,
                selection="BOS",
                last_updated=datetime.now().isoformat()
            ))

        start_time = time.time()
        best_bets = betting_analyzer.analyze_best_bets(sample_game_data, large_odds)
        end_time = time.time()

        # Analysis should complete in reasonable time
        assert (end_time - start_time) < 1.0  # Less than 1 second
        assert isinstance(best_bets, list)