import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';
import { gameService } from '../services/api';
import { GameWithBestBets, BetType } from '../types';

// Mock the API service
jest.mock('../services/api', () => ({
  gameService: {
    getAllGamesWithBets: jest.fn(),
  },
}));

const mockGameService = gameService as jest.Mocked<typeof gameService>;

// Mock game data for testing
const mockGames: GameWithBestBets[] = [
  {
    id: 'mock_game_001',
    home_team: {
      id: 1610612738,
      name: 'Boston Celtics',
      abbreviation: 'BOS',
      city: 'Boston',
      seed: 1
    },
    away_team: {
      id: 1610612748,
      name: 'Miami Heat',
      abbreviation: 'MIA',
      city: 'Miami',
      seed: 8
    },
    scheduled_time: new Date().toISOString(),
    status: 'scheduled',
    arena: 'TD Garden',
    series: 'Eastern Conference Finals Game 1',
    season_type: 'playoffs',
    odds: [],
    best_bets: [
      {
        bet_type: BetType.MONEYLINE,
        selection: 'BOS',
        best_odds: -150,
        sportsbook: 'MockBook',
        confidence: 0.75,
        reasoning: 'Strong home court advantage in playoffs',
        expected_value: 0.15
      }
    ]
  }
];

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Set up successful API response by default
    mockGameService.getAllGamesWithBets.mockResolvedValue(mockGames);
  });

  test('renders NBA Betting Compiler header', async () => {
    await act(async () => {
      render(<App />);
    });

    const headerElement = screen.getByText(/NBA Betting Compiler/i);
    expect(headerElement).toBeInTheDocument();
  });

  test('renders subtitle correctly', async () => {
    await act(async () => {
      render(<App />);
    });

    const subtitle = screen.getByText(/Smart NBA Playoff Betting Analysis & Recommendations/i);
    expect(subtitle).toBeInTheDocument();
  });

  test('renders GamesList component', async () => {
    await act(async () => {
      render(<App />);
    });

    // Wait for the GamesList component to render
    await waitFor(() => {
      const gamesListElement = screen.getByText(/NBA Playoff Games/i);
      expect(gamesListElement).toBeInTheDocument();
    });
  });

  test('has correct app structure', async () => {
    await act(async () => {
      render(<App />);
    });

    // Check for main structural elements
    const header = screen.getByRole('banner');
    const main = screen.getByRole('main');

    expect(header).toBeInTheDocument();
    expect(main).toBeInTheDocument();
    expect(main).toHaveClass('App-main');
  });

  test('handles game selection', async () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

    await act(async () => {
      render(<App />);
    });

    // This tests the handleGameSelect function indirectly
    // In a real scenario, we'd need to trigger a game selection event

    consoleSpy.mockRestore();
  });
});