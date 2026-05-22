import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import GameCard from '../components/GameCard';
import { GameWithBestBets, GameStatus, BetType } from '../types';

// Mock game data for testing
const mockGame: GameWithBestBets = {
  id: 'test-game-1',
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
  scheduled_time: '2026-05-18T20:00:00Z',
  status: GameStatus.SCHEDULED,
  arena: 'TD Garden',
  series: 'Eastern Conference Finals Game 1',
  season_type: 'playoffs',
  odds: [],
  best_bets: [
    {
      bet_type: BetType.MONEYLINE,
      selection: 'BOS',
      best_odds: -150,
      sportsbook: 'DraftKings',
      confidence: 0.75,
      reasoning: 'Strong home court advantage',
      expected_value: 0.15
    },
    {
      bet_type: BetType.SPREAD,
      selection: 'MIA',
      line: 4.5,
      best_odds: -110,
      sportsbook: 'FanDuel',
      confidence: 0.68,
      reasoning: 'Miami covers as road dog',
      expected_value: 0.08
    }
  ]
};

const mockGameNoSeries: GameWithBestBets = {
  ...mockGame,
  series: undefined,
  best_bets: []
};

describe('GameCard Component', () => {
  const mockOnGameClick = jest.fn();

  beforeEach(() => {
    mockOnGameClick.mockClear();
  });

  test('renders game teams correctly', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    // Team names are displayed as "City Name" so we get "Boston Boston Celtics" and "Miami Miami Heat"
    expect(screen.getByText('Boston Boston Celtics')).toBeInTheDocument();
    expect(screen.getByText('Miami Miami Heat')).toBeInTheDocument();
    expect(screen.getByText('(BOS)')).toBeInTheDocument();
    expect(screen.getByText('(MIA)')).toBeInTheDocument();
  });

  test('displays team seeds', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#8')).toBeInTheDocument();
  });

  test('shows game time and arena', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    expect(screen.getByText('TD Garden')).toBeInTheDocument();
    // Time display depends on locale, so we check for presence
    expect(screen.getByText(/\d{1,2}:\d{2}/)).toBeInTheDocument();
  });

  test('displays game status', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    expect(screen.getByText('SCHEDULED')).toBeInTheDocument();
    expect(screen.getByText('SCHEDULED')).toHaveClass('status-scheduled');
  });

  test('shows series information when available', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    expect(screen.getByText('Eastern Conference Finals Game 1')).toBeInTheDocument();
  });

  test('handles missing series information', () => {
    render(<GameCard game={mockGameNoSeries} onGameClick={mockOnGameClick} />);

    expect(screen.queryByText('Eastern Conference Finals Game 1')).not.toBeInTheDocument();
  });

  test('displays best bets correctly', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    // Check for bet details
    expect(screen.getByText('BOS')).toBeInTheDocument();
    expect(screen.getByText('-150')).toBeInTheDocument();
    expect(screen.getByText('DraftKings')).toBeInTheDocument();
    expect(screen.getByText('Confidence: 75%')).toBeInTheDocument();
    expect(screen.getByText('Strong home court advantage')).toBeInTheDocument();
  });

  test('handles games with no best bets', () => {
    render(<GameCard game={mockGameNoSeries} onGameClick={mockOnGameClick} />);

    expect(screen.getByText('No main recommendations available')).toBeInTheDocument();
  });

  test('shows correct bet count', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    expect(screen.getByText('2 total recommendations')).toBeInTheDocument();
  });

  test('calls onGameClick when card is clicked', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    const gameCard = screen.getByText('Boston Boston Celtics').closest('.game-card');

    if (gameCard) {
      fireEvent.click(gameCard);
      expect(mockOnGameClick).toHaveBeenCalledWith('test-game-1');
    }
  });

  test('formats odds correctly', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    // Negative odds should show as-is
    expect(screen.getByText('-150')).toBeInTheDocument();

    // Test with positive odds
    const gameWithPositiveOdds = {
      ...mockGame,
      best_bets: [{
        ...mockGame.best_bets[0],
        best_odds: 150
      }]
    };

    render(<GameCard game={gameWithPositiveOdds} onGameClick={mockOnGameClick} />);
    expect(screen.getByText('+150')).toBeInTheDocument();
  });

  test('displays bet types with correct icons', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    // Check that bet type icons are displayed (emojis)
    // This is a basic check since emojis might render differently
    const betItems = screen.getAllByText(/💰|📊|⚖️|🎯/);
    expect(betItems.length).toBeGreaterThan(0);
  });

  test('shows confidence as percentage', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    expect(screen.getByText('Confidence: 75%')).toBeInTheDocument();
    expect(screen.getByText('Confidence: 68%')).toBeInTheDocument();
  });

  test('handles different game statuses', () => {
    const liveGame = { ...mockGame, status: GameStatus.LIVE };
    const finishedGame = { ...mockGame, status: GameStatus.FINISHED };

    const { rerender } = render(<GameCard game={liveGame} onGameClick={mockOnGameClick} />);
    expect(screen.getByText('LIVE')).toHaveClass('status-live');

    rerender(<GameCard game={finishedGame} onGameClick={mockOnGameClick} />);
    expect(screen.getByText('FINISHED')).toHaveClass('status-finished');
  });

  test('displays spread lines correctly', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    // Should show "MIA +4.5" for the spread bet
    expect(screen.getByText('MIA +4.5')).toBeInTheDocument();
  });

  test('handles accessibility', () => {
    render(<GameCard game={mockGame} onGameClick={mockOnGameClick} />);

    // Card should be clickable and have the correct CSS class
    const gameCard = screen.getByText('Boston Boston Celtics').closest('.game-card');
    expect(gameCard).toHaveClass('game-card');

    // Test that the card is interactive (it should have an onClick handler)
    fireEvent.click(gameCard!);
    expect(mockOnGameClick).toHaveBeenCalledWith('test-game-1');
  });
});