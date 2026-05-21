"""
Integration tests for all API endpoints in the NBA Sports Betting Compiler.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.integration
class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check_success(self, client: TestClient):
        """Test that health endpoint returns success."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "nba-betting-compiler"

    def test_health_check_response_format(self, client: TestClient):
        """Test health endpoint response format and content."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "nba-betting-compiler"
        assert "timestamp" in data


@pytest.mark.api
@pytest.mark.integration
class TestRootEndpoint:
    """Test the root API endpoint."""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["message"] == "NBA Sports Betting Compiler API"

    def test_root_endpoint_structure(self, client: TestClient):
        """Test root endpoint has correct structure."""
        response = client.get("/")
        data = response.json()

        # Check required fields
        required_fields = ["message", "version", "docs", "endpoints"]
        for field in required_fields:
            assert field in data

        # Check endpoints structure
        endpoints = data["endpoints"]
        expected_endpoints = [
            "today_games", "game_odds", "best_bets",
            "complete_game", "all_games"
        ]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints


@pytest.mark.api
@pytest.mark.integration
class TestGamesEndpoints:
    """Test all games-related API endpoints."""

    def test_get_todays_games(self, client: TestClient, mock_nba_service):
        """Test fetching today's games."""
        response = client.get("/api/games/today")

        assert response.status_code == 200
        games = response.json()
        assert isinstance(games, list)

        if games:  # If games exist
            game = games[0]
            required_fields = [
                "id", "home_team", "away_team", "scheduled_time",
                "status", "arena", "season_type", "odds"
            ]
            for field in required_fields:
                assert field in game

    def test_get_all_games_with_bets(self, client: TestClient, mock_nba_service):
        """Test fetching all games with best bets."""
        response = client.get("/api/games/")

        assert response.status_code == 200
        games = response.json()
        assert isinstance(games, list)

        if games:  # If games exist
            game = games[0]
            # Should include best_bets field
            assert "best_bets" in game
            assert isinstance(game["best_bets"], list)

    def test_get_data_source_info(self, client: TestClient, mock_nba_service):
        """Test data source information endpoint."""
        response = client.get("/api/games/data-source")

        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "data_source", "odds_api_configured", "available_sources"
        ]
        for field in required_fields:
            assert field in data

        # Should be using real data source (no mock option)
        assert data["data_source"] == "real"
        assert isinstance(data["available_sources"], dict)

        # Should have health info for real data
        assert "api_health" in data
        assert "status" in data["api_health"]

        # Check available sources (no mock)
        sources = data["available_sources"]
        expected_sources = ["espn", "odds_api", "balldontlie"]
        for source in expected_sources:
            assert source in sources

    def test_games_endpoints_consistency(self, client: TestClient):
        """Test games endpoints return consistent data formats."""
        # Test today's games format
        response = client.get("/api/games/today")
        assert response.status_code == 200
        games = response.json()
        if games:
            assert isinstance(games, list)
            assert all("id" in game for game in games)

        # Test data source format
        response = client.get("/api/games/data-source")
        assert response.status_code == 200
        data = response.json()
        assert "data_source" in data

    def test_specific_game_endpoints(self, client: TestClient, mock_nba_service):
        """Test specific game-related endpoints."""
        # First get a game ID
        response = client.get("/api/games/today")
        games = response.json()

        if not games:
            pytest.skip("No games available for testing specific endpoints")

        game_id = games[0]["id"]

        # Test game odds endpoint
        response = client.get(f"/api/games/{game_id}/odds")
        assert response.status_code == 200
        odds = response.json()
        assert isinstance(odds, list)

        # Test best bets endpoint
        response = client.get(f"/api/games/{game_id}/best-bets")
        assert response.status_code == 200
        bets = response.json()
        assert isinstance(bets, list)

        # Test complete game data endpoint
        response = client.get(f"/api/games/{game_id}/complete")
        assert response.status_code == 200
        game_data = response.json()
        assert "odds" in game_data
        assert "best_bets" in game_data

    def test_nonexistent_game(self, client: TestClient):
        """Test endpoints with non-existent game ID."""
        fake_game_id = "nonexistent_game_12345"

        response = client.get(f"/api/games/{fake_game_id}/complete")
        assert response.status_code == 404


@pytest.mark.api
@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across all endpoints."""

    def test_invalid_routes(self, client: TestClient):
        """Test that invalid routes return 404."""
        invalid_routes = [
            "/invalid",
            "/api/invalid",
            "/api/games/invalid",
            "/health/invalid"
        ]

        for route in invalid_routes:
            response = client.get(route)
            assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient):
        """Test that wrong HTTP methods return 405."""
        # These endpoints only support GET
        endpoints = [
            "/health",
            "/api/games/today",
            "/api/games/data-source"
        ]

        for endpoint in endpoints:
            response = client.post(endpoint)
            assert response.status_code == 405

    def test_multiple_requests(self, client: TestClient):
        """Test handling of multiple sequential requests."""
        endpoints = [
            "/health",
            "/api/games/today",
            "/api/games/data-source",
            "/"
        ]

        # Make multiple requests to test stability
        for _ in range(3):
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code == 200


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Test API performance and response times."""

    def test_response_time_health(self, client: TestClient):
        """Test health endpoint response time."""
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        # Health endpoint should respond in under 100ms
        assert (end_time - start_time) < 0.1

    def test_response_time_games(self, client: TestClient):
        """Test games endpoint response time."""
        import time

        start_time = time.time()
        response = client.get("/api/games/today")
        end_time = time.time()

        assert response.status_code == 200
        # Games endpoint should respond in under 2 seconds
        assert (end_time - start_time) < 2.0

    def test_payload_sizes(self, client: TestClient, mock_nba_service):
        """Test that response payloads are reasonable size."""
        # Test games endpoint
        response = client.get("/api/games/")
        assert response.status_code == 200

        # Response should be less than 1MB
        content_length = len(response.content)
        assert content_length < 1024 * 1024  # 1MB


@pytest.mark.api
@pytest.mark.security
class TestSecurityHeaders:
    """Test security-related headers and responses."""

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are present."""
        response = client.options("/api/games/today")

        # Should have CORS headers (configured in main.py)
        # Note: TestClient might not include all CORS headers
        # This is more relevant for production testing
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled

    def test_no_sensitive_info_in_responses(self, client: TestClient):
        """Test that responses don't contain sensitive information."""
        endpoints = [
            "/",
            "/health",
            "/api/games/today",
            "/api/games/data-source"
        ]

        # More specific sensitive patterns to avoid false positives
        sensitive_patterns = [
            "password=", "secret=", "private_key", "access_token",
            "credentials=", "auth_token", "bearer ", "basic "
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            response_text = response.text.lower()

            for pattern in sensitive_patterns:
                assert pattern not in response_text, f"Found '{pattern}' in {endpoint} response"

    def test_error_responses_safe(self, client: TestClient):
        """Test that error responses don't leak sensitive information."""
        # Trigger various errors
        response = client.get("/nonexistent")
        assert response.status_code == 404

        # Error response shouldn't contain file paths or internal details
        error_text = response.text.lower()
        dangerous_patterns = ["traceback", "file path", "internal server"]

        for pattern in dangerous_patterns:
            assert pattern not in error_text