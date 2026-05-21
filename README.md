# NBA Sports Betting Compiler

A full-stack application that compiles the best betting odds and recommendations for NBA playoff games.

## Project Structure

```
nba-sports-betting-compiler/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── api/            # API routes
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Container config
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API calls
│   │   └── utils/         # Utility functions
│   ├── package.json       # Node dependencies
│   └── public/            # Static assets
└── README.md              # This file
```

## Features

- Real-time NBA playoff schedule
- Best betting odds compilation
- Multiple sportsbook integration
- Clean, responsive UI
- Live odds updates

## Getting Started

### Quick Start (Recommended)
```bash
# Start both frontend and backend
make dev

# Stop both servers gracefully  
make stop
```

### Manual Setup

#### Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (React)
```bash
cd frontend
npm install
npm start
```

#### Docker (Alternative)
```bash
docker-compose up --build
```

### Testing
```bash
# Test all API endpoints
./scripts/test-api.sh
```

## API Endpoints

- `GET /api/games/today` - Today's playoff games
- `GET /api/games/{game_id}/odds` - Betting odds for a specific game
- `GET /api/best-bets/{game_id}` - Compiled best bets for a game