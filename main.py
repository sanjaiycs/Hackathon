from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import asyncio
from datetime import datetime, timedelta

from app.buyer_agent import YourBuyerAgent

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Session storage with expiration
sessions = {}

class NegotiationInput(BaseModel):
    product: str
    budget: int
    seller_message: str
    session_id: str | None = None

class ResetInput(BaseModel):
    session_id: str

@app.on_event("startup")
async def startup_event():
    async def cleanup_sessions():
        while True:
            now = datetime.now()
            expired = [sid for sid, session in sessions.items() 
                      if now - session['last_active'] > timedelta(hours=1)]
            for sid in expired:
                del sessions[sid]
            await asyncio.sleep(3600)
    
    asyncio.create_task(cleanup_sessions())

@app.post("/api/negotiate")
async def negotiate(input_data: NegotiationInput):
    try:
        if input_data.budget <= 0:
            raise HTTPException(status_code=400, detail="Budget must be positive")
        
        sid = input_data.session_id or str(uuid.uuid4())

        if sid not in sessions:
            sessions[sid] = {
                'agent': YourBuyerAgent(product=input_data.product, budget=input_data.budget),
                'last_active': datetime.now()
            }
        
        session = sessions[sid]
        session['last_active'] = datetime.now()
        
        response = session['agent'].negotiate(
            input_data.product,
            input_data.budget,
            input_data.seller_message
        )
        
        return JSONResponse({
            "session_id": sid,
            "response": {
                "action": response.action,
                "message": response.message,
                "offer_price": response.offer_price
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
async def reset(input_data: ResetInput):
    if input_data.session_id in sessions:
        del sessions[input_data.session_id]
    return {"status": "reset"}