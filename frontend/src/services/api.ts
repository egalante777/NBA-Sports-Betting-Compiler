import axios from 'axios';
import { Game, GameWithBestBets, Odds, BestBet } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const gameService = {
  // Get today's games
  getTodaysGames: async (): Promise<Game[]> => {
    const response = await api.get('/api/games/today');
    return response.data;
  },

  // Get odds for a specific game
  getGameOdds: async (gameId: string): Promise<Odds[]> => {
    const response = await api.get(`/api/games/${gameId}/odds`);
    return response.data;
  },

  // Get best bets for a specific game
  getBestBets: async (gameId: string): Promise<BestBet[]> => {
    const response = await api.get(`/api/games/${gameId}/best-bets`);
    return response.data;
  },

  // Get complete game data (game + odds + best bets)
  getCompleteGameData: async (gameId: string): Promise<GameWithBestBets> => {
    const response = await api.get(`/api/games/${gameId}/complete`);
    return response.data;
  },

  // Get all games with their best bets
  getAllGamesWithBets: async (): Promise<GameWithBestBets[]> => {
    const response = await api.get('/api/games/');
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;