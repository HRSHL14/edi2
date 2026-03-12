from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection
from chatbot.chatbot_engine import ChatbotEngine
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Groundwater Data API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ChatbotEngine()

class ChatRequest(BaseModel):
    query: str
    provider: str = "groq" # Default to groq

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = engine.handle_query(request.query, provider=request.provider)
        print(f"DEBUG: Chatbot Response for '{request.query}' [{request.provider}]: {response}")
        return response
    except Exception as e:
        print(f"DEBUG: Chatbot Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/districts", response_model=List[str])
def get_districts():
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed. Please ensure PostgreSQL is running on localhost:5432.")
        cur = conn.cursor()
        cur.execute("SELECT district_name FROM districts ORDER BY district_name")
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals() and conn: conn.close()

@app.get("/talukas/{district}", response_model=List[str])
def get_talukas(district: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.taluka_name 
            FROM talukas t
            JOIN districts d ON t.district_id = d.district_id
            WHERE d.district_name ILIKE %s
            ORDER BY t.taluka_name
        """, (district,))
        rows = cur.fetchall()
        return [row[0] for row in rows]
    finally:
        conn.close()

@app.get("/taluka/{name}", response_model=Dict)
def get_taluka(name: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM groundwater_data
            WHERE taluka ILIKE %s
            LIMIT 1
        """, (name,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Taluka not found")
            
        return dict({
            "taluka": row.get("taluka"),
            "district": row.get("district"),
            "rainfall": row.get("rainfall"),
            "recharge_total": row.get("total_recharge"),
            "extraction": row.get("groundwater_extraction_total"),
            "stage": row.get("stage_of_extraction"),
            "category": row.get("category")
        })
    finally:
        conn.close()

@app.get("/district-summary/{district}", response_model=Dict)
def get_district_summary(district: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                COUNT(*) as taluka_count,
                AVG(rainfall) as avg_rainfall,
                SUM(total_recharge) as total_recharge_sum,
                SUM(groundwater_extraction_total) as total_extraction_sum,
                AVG(stage_of_extraction) as avg_stage
            FROM groundwater_data
            WHERE district ILIKE %s
        """, (district,))
        row = cur.fetchone()
        if not row or row['taluka_count'] == 0:
            raise HTTPException(status_code=404, detail="District not found or empty")
            
        return dict({
            "district": district,
            "talukas_analyzed": row.get("taluka_count"),
            "avg_rainfall": row.get("avg_rainfall"),
            "total_recharge": row.get("total_recharge_sum"),
            "total_extraction": row.get("total_extraction_sum"),
            "avg_stage_of_extraction": row.get("avg_stage")
        })
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
