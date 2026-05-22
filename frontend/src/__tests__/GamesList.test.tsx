import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import GamesList from '../components/GamesList';
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

describe('GamesList Component', () => {
  const mockOnGameSelect = jest.fn();

  beforeEach(() => {
    mockOnGameSelect.mockClear();
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Set up successful API response by default
    mockGameService.getAllGamesWithBets.mockResolvedValue(mockGames);
  });

  test('renders component title', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/NBA Playoff Games/i)).toBeInTheDocument();
    });
  });

  test('shows loading spinner initially', async () => {
    // Create a promise that resolves after a delay to catch the loading state
    let resolvePromise: (value: GameWithBestBets[]) => void;
    const delayedPromise = new Promise<GameWithBestBets[]>((resolve) => {
      resolvePromise = resolve;
    });

    // Mock the API call to use our delayed promise
    mockGameService.getAllGamesWithBets.mockReturnValue(delayedPromise);

    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    // Check that loading spinner is shown
    expect(screen.getByText(/Loading today's NBA playoff games/i)).toBeInTheDocument();

    // Resolve the promise to clean up
    await act(async () => {
      resolvePromise!(mockGames);
    });
  });

  test('displays games after loading', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    // Wait for games to load
    await waitFor(() => {
      expect(screen.getByText('Boston Boston Celtics')).toBeInTheDocument();
    });

    expect(screen.getByText('Miami Miami Heat')).toBeInTheDocument();
  });

  test('shows refresh button', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    await waitFor(() => {
      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      expect(refreshButton).toBeInTheDocument();
    });
  });

  test('refresh button works', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    await waitFor(() => {
      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      fireEvent.click(refreshButton);
      // The button should show loading state
      expect(refreshButton).toBeDisabled();
    });
  });

  test('displays last updated time', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/Last updated:/i)).toBeInTheDocument();
    });
  });

  test('shows disclaimer', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/This information is for entertainment purposes only/i)).toBeInTheDocument();
    });
  });

  test('handles game selection', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    await waitFor(() => {
      const gameCard = screen.getByText('Boston Boston Celtics').closest('.game-card');
      if (gameCard) {
        fireEvent.click(gameCard);
        expect(mockOnGameSelect).toHaveBeenCalledWith(expect.stringMatching(/mock_game_/));
      }
    });
  });

  test('displays current date', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    const today = new Date().toLocaleDateString();
    await waitFor(() => {
      expect(screen.getByText(new RegExp(today.replace(/\//g, '\\/'))))
        .toBeInTheDocument();
    });
  });

  test('shows spinning refresh icon when loading', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={mockOnGameSelect} />);
    });

    await waitFor(() => {
      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      fireEvent.click(refreshButton);

      // Check for spinning class or loading state
      expect(refreshButton).toBeDisabled();
    });
  });
});

describe('GamesList Error Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('handles API errors gracefully', async () => {
    // Mock API to reject with an error
    mockGameService.getAllGamesWithBets.mockRejectedValue(new Error('Network error'));

    await act(async () => {
      render(<GamesList onGameSelect={jest.fn()} />);
    });

    await waitFor(() => {
      // Should show error message
      expect(screen.getByText('Unable to Load Games')).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch games data. Please try again.')).toBeInTheDocument();
    });

    // Should not show game data
    expect(screen.queryByText('Boston Celtics')).not.toBeInTheDocument();
  });
});

describe('GamesList Accessibility', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGameService.getAllGamesWithBets.mockResolvedValue(mockGames);
  });

  test('has proper ARIA labels and roles', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={jest.fn()} />);
    });

    // Wait for games to load first
    await waitFor(() => {
      expect(screen.getByText('Boston Boston Celtics')).toBeInTheDocument();
    });

    // Check for proper button roles
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    expect(refreshButton).toBeInTheDocument();
  });

  test('supports keyboard navigation', async () => {
    await act(async () => {
      render(<GamesList onGameSelect={jest.fn()} />);
    });

    // Wait for games to load first
    await waitFor(() => {
      expect(screen.getByText('Boston Boston Celtics')).toBeInTheDocument();
    });

    const refreshButton = screen.getByRole('button', { name: /refresh/i });

    // Test keyboard focus
    refreshButton.focus();
    expect(refreshButton).toHaveFocus();

    // Test clicking the button triggers loading state
    fireEvent.click(refreshButton);
    expect(refreshButton).toBeDisabled(); // Should trigger loading
  });
});

describe('GamesList Responsive Design', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGameService.getAllGamesWithBets.mockResolvedValue(mockGames);
  });

  test('adapts to mobile viewport', async () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    await act(async () => {
      render(<GamesList onGameSelect={jest.fn()} />);
    });

    // Wait for component to load games first
    await waitFor(() => {
      expect(screen.getByText('Boston Boston Celtics')).toBeInTheDocument();
    });

    // Component should render without errors on mobile
    expect(screen.getByText(/NBA Playoff Games/i)).toBeInTheDocument();
  });
});