from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict
import os

from game_engine import GameEngine
from renderer import GameRenderer

app = FastAPI(title="Trash Kart Racer API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Game state storage
active_games: Dict[str, GameEngine] = {}
player_sessions: Dict[str, Dict] = {}  # player_id -> {game_id, best_score}
game_renderer = GameRenderer()

class GameAction(BaseModel):
    action: str  # 'gas', 'brake', 'boost'
    player_id: str

class NewGameRequest(BaseModel):
    player_id: str

@app.get("/", response_class=HTMLResponse)
async def get_home():
    return FileResponse("templates/index.html")

@app.get("/api/game/state/{game_id}")
async def get_game_state(game_id: str):
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    state = game.get_game_state()
    
    return {
        "game_id": game_id,
        "state": state,
        "alive": state["player"]["alive"],
        "distance": state["player"]["distance"]
    }

@app.post("/api/game/new")
async def create_new_game(req: NewGameRequest):
    game_id = str(uuid.uuid4())
    game = GameEngine()
    
    active_games[game_id] = game
    
    # Initialize or update player session
    if req.player_id not in player_sessions:
        player_sessions[req.player_id] = {
            "current_game": game_id,
            "best_score": 0
        }
    else:
        player_sessions[req.player_id]["current_game"] = game_id
    
    return {
        "game_id": game_id,
        "message": "Game created successfully"
    }

@app.post("/api/game/action")
async def perform_action(action: GameAction):
    if action.player_id not in player_sessions:
        raise HTTPException(status_code=404, detail="Player not found")
    
    game_id = player_sessions[action.player_id]["current_game"]
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    game.update(action.action)
    
    # Update best score
    state = game.get_game_state()
    distance_score = int(state["player"]["distance"] // 5)
    if distance_score > player_sessions[action.player_id]["best_score"]:
        player_sessions[action.player_id]["best_score"] = distance_score
    
    return {
        "success": True,
        "alive": state["player"]["alive"],
        "distance": distance_score,
        "best_score": player_sessions[action.player_id]["best_score"]
    }

@app.get("/api/game/render/{game_id}")
async def render_game_frame(game_id: str):
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    state = game.get_game_state()
    
    # Render the frame
    frame = game_renderer.render_frame(state)
    
    # Save to bytes
    from io import BytesIO
    img_byte_arr = BytesIO()
    frame.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return Response(content=img_byte_arr.read(), media_type="image/png")

@app.get("/api/player/stats/{player_id}")
async def get_player_stats(player_id: str):
    if player_id not in player_sessions:
        return {
            "best_score": 0,
            "games_played": 0,
            "current_game": None
        }
    
    session = player_sessions[player_id]
    return {
        "best_score": session["best_score"],
        "games_played": len([g for g in active_games.values() if not g.player.alive]),
        "current_game": session.get("current_game")
    }

@app.websocket("/ws/game/{game_id}")
async def websocket_game(websocket: WebSocket, game_id: str):
    await websocket.accept()
    
    if game_id not in active_games:
        await websocket.close(code=1000, reason="Game not found")
        return
    
    try:
        while True:
            # Receive action from client
            data = await websocket.receive_json()
            action = data.get("action")
            player_id = data.get("player_id")
            
            if action and player_id:
                game = active_games[game_id]
                game.update(action)
                
                # Send updated state
                state = game.get_game_state()
                await websocket.send_json({
                    "type": "game_state",
                    "state": state,
                    "alive": state["player"]["alive"],
                    "distance": int(state["player"]["distance"] // 5)
                })
                
                # Send render if needed
                if data.get("need_render"):
                    frame = game_renderer.render_frame(state, show_death=not state["player"]["alive"])
                    
                    from io import BytesIO
                    img_byte_arr = BytesIO()
                    frame.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    
                    await websocket.send_bytes(img_byte_arr.read())
            
            await asyncio.sleep(0.1)  # Prevent flooding
            
    except WebSocketDisconnect:
        print(f"Client disconnected from game {game_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))

# Admin endpoints
@app.get("/admin/games")
async def list_active_games():
    return {
        "active_games": len(active_games),
        "active_players": len(player_sessions),
        "games": list(active_games.keys())[:10]
    }

@app.delete("/admin/game/{game_id}")
async def delete_game(game_id: str):
    if game_id in active_games:
        del active_games[game_id]
        return {"message": f"Game {game_id} deleted"}
    return {"message": "Game not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
