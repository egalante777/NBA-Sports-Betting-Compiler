"""
Test configuration and fixtures for NBA Sports Betting Compiler backend tests.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.services.data_service_factory import DataServiceFactory
from app.services.real_nba_service import RealNBAService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for FastAPI application.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for FastAPI application.
    """
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client


@pytest.fixture
def mock_nba_service(monkeypatch):
    """
    Create a properly mocked NBA service for testing that avoids real API calls.
    """
    from unittest.mock import AsyncMock, Mock, patch
    from app.models.game import Game, Team, GameStatus, Odds, BetType
    from datetime import datetime
    import httpx

    # Create mock service with API key for testing
    service = RealNBAService()
    service.odds_api_key = "test_api_key_for_testing"  # Override for tests

    # Create realistic mock odds data with varied confidence scores
    def create_mock_odds_response():
        return [
            {
                "id": "test_game_001",
                "sport_key": "basketball_nba",
                "sport_title": "NBA",
                "commence_time": "2026-05-20T00:00:00Z",
                "home_team": "Boston Celtics",
                "away_team": "Miami Heat",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "last_update": "2026-05-19T15:00:00Z",
                        "markets": [
                            {
                                "key": "h2h",
                                "last_update": "2026-05-19T15:00:00Z",
                                "outcomes": [
                                    {"name": "Boston Celtics", "price": -150},
                                    {"name": "Miami Heat", "price": 130}
                                ]
                            },
                            {
                                "key": "spreads",
                                "last_update": "2026-05-19T15:00:00Z",
                                "outcomes": [
                                    {"name": "Boston Celtics", "price": -110, "point": -3.5},
                                    {"name": "Miami Heat", "price": -110, "point": 3.5}
                                ]
                            },
                            {
                                "key": "totals",
                                "last_update": "2026-05-19T15:00:00Z",
                                "outcomes": [
                                    {"name": "Over", "price": -105, "point": 215.5},
                                    {"name": "Under", "price": -115, "point": 215.5}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "fanduel",
                        "title": "FanDuel",
                        "last_update": "2026-05-19T15:00:00Z",
                        "markets": [
                            {
                                "key": "h2h",
                                "last_update": "2026-05-19T15:00:00Z",
                                "outcomes": [
                                    {"name": "Boston Celtics", "price": -145},
                                    {"name": "Miami Heat", "price": 125}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]

    # Mock ESPN API response
    def create_mock_espn_response():
        return {
            "events": [
                {
                    "id": "401873341",
                    "date": "2026-05-20T00:00:00Z",
                    "season": {"type": 3, "slug": "post-season"},
                    "competitions": [{
                        "competitors": [
                            {
                                "homeAway": "home",
                                "team": {
                                    "id": "1",
                                    "displayName": "Boston Celtics",
                                    "abbreviation": "BOS",
                                    "location": "Boston",
                                    "logo": "https://example.com/logo.png"
                                }
                            },
                            {
                                "homeAway": "away",
                                "team": {
                                    "id": "2",
                                    "displayName": "Miami Heat",
                                    "abbreviation": "MIA",
                                    "location": "Miami",
                                    "logo": "https://example.com/logo.png"
                                }
                            }
                        ],
                        "venue": {"fullName": "TD Garden"}
                    }],
                    "status": {"type": {"name": "STATUS_SCHEDULED"}}
                }
            ]
        }

    # Mock the HTTP client to avoid real API calls
    async def mock_httpx_get(self, url, params=None, **kwargs):
        mock_response = Mock()

        if "the-odds-api.com" in url:
            # Mock Odds API response
            mock_response.status_code = 200
            mock_response.json.return_value = create_mock_odds_response()
        elif "espn.com" in url:
            # Mock ESPN API response
            mock_response.status_code = 200
            mock_response.json.return_value = create_mock_espn_response()
        else:
            # Other APIs
            mock_response.status_code = 200
            mock_response.json.return_value = {}

        return mock_response

    # Patch the httpx.AsyncClient.get method
    monkeypatch.setattr("httpx.AsyncClient.get", mock_httpx_get)

    async def mock_check_api_health():
        return {
            'espn': True,
            'odds_api': True,
            'balldontlie': True
        }

    service.check_api_health = mock_check_api_health

    # Mock the factory to return our mocked service
    monkeypatch.setattr(DataServiceFactory, 'get_nba_service', lambda: service)

    # Also patch the module-level service in the API
    from app.api import games
    monkeypatch.setattr(games, 'nba_service', service)

    return service


@pytest.fixture
def sample_game_data():
    """
    Sample game data for testing.
    """
    from datetime import datetime
    from app.models.game import Game, Team, GameStatus

    return Game(
        id="test_game_001",
        home_team=Team(
            id=1610612738,
            name="Boston Celtics",
            abbreviation="BOS",
            city="Boston",
            seed=1
        ),
        away_team=Team(
            id=1610612748,
            name="Miami Heat",
            abbreviation="MIA",
            city="Miami",
            seed=8
        ),
        scheduled_time=datetime.now().isoformat(),
        status=GameStatus.SCHEDULED,
        arena="TD Garden",
        series="Eastern Conference Finals Game 1",
        season_type="playoffs",
        odds=[]
    )


@pytest.fixture
def sample_odds_data():
    """
    Sample betting odds data for testing.
    """
    from datetime import datetime
    from app.models.game import Odds, BetType

    return [
        Odds(
            sportsbook="TestBook",
            bet_type=BetType.MONEYLINE,
            odds=-150,
            selection="BOS",
            last_updated=datetime.now().isoformat()
        ),
        Odds(
            sportsbook="TestBook",
            bet_type=BetType.SPREAD,
            line=-4.5,
            odds=-110,
            selection="BOS",
            last_updated=datetime.now().isoformat()
        )
    ]


@pytest.fixture
def sample_best_bets():
    """
    Sample best bet recommendations for testing.
    """
    from app.models.game import BestBet, BetType

    return [
        BestBet(
            bet_type=BetType.MONEYLINE,
            selection="BOS",
            best_odds=-150,
            sportsbook="TestBook",
            confidence=0.75,
            reasoning="Strong home court advantage",
            expected_value=0.25
        )
    ]


@pytest.fixture
def betting_analyzer():
    """
    Betting analyzer instance for testing.
    """
    from app.services.betting_analyzer import BettingAnalyzer
    analyzer = BettingAnalyzer()

    # Override confidence weights to avoid division by zero
    analyzer.confidence_weights = {
        'odds_value': 0.4,
        'line_movement': 0.3,
        'market_consensus': 0.3
    }

    return analyzer


# Pytest markers for test categorization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.api = pytest.mark.api
pytest.mark.security = pytest.mark.security
pytest.mark.slow = pytest.mark.slow
pytest.mark.external = pytest.mark.external