from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .api.games import router as games_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="NBA Sports Betting Compiler API",
    description="API for compiling NBA playoff betting odds and recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(games_router)

@app.get("/")
async def root():
    return {
        "message": "NBA Sports Betting Compiler API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "today_games": "/api/games/today",
            "game_odds": "/api/games/{game_id}/odds",
            "best_bets": "/api/games/{game_id}/best-bets",
            "complete_game": "/api/games/{game_id}/complete",
            "all_games": "/api/games/"
        }
    }

@app.get("/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "nba-betting-compiler",
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )