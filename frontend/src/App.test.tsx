import React from 'react';
import { render, screen, act } from '@testing-library/react';
import App from './App';
import { gameService } from './services/api';

// Mock the API service
jest.mock('./services/api', () => ({
  gameService: {
    getAllGamesWithBets: jest.fn(),
  },
}));

const mockGameService = gameService as jest.Mocked<typeof gameService>;

test('renders NBA Betting Compiler app', async () => {
  // Set up successful API response
  mockGameService.getAllGamesWithBets.mockResolvedValue([]);

  await act(async () => {
    render(<App />);
  });

  // Look for the main heading
  const headingElement = screen.getByText(/NBA Betting Compiler/i);
  expect(headingElement).toBeInTheDocument();

  // Look for the subtitle
  const subtitleElement = screen.getByText(/Smart NBA Playoff Betting Analysis/i);
  expect(subtitleElement).toBeInTheDocument();
});
