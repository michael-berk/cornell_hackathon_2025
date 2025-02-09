from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
import asyncio

# Set the file path
CSV_FILE = "/Users/michael.berk/dev/cornell_hackathon/cornell_hackathon_2025/scratch/eye_tracking/streamlit/gaze_data.csv"

# Ensure directory exists
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

# Initialize FastAPI
app = FastAPI()
lock = asyncio.Lock()  # Prevent race conditions

class GazeData(BaseModel):
    timestamp: str
    x: float
    y: float

@app.post("/save_gaze_data")
async def save_gaze_data(data: GazeData):
    """Append gaze data to CSV asynchronously."""
    async with lock:
        df = pd.DataFrame([[data.timestamp, data.x, data.y]], columns=["timestamp", "x", "y"])
        df.to_csv(CSV_FILE, mode="a", header=not os.path.exists(CSV_FILE), index=False)
    return {"message": "Data saved"}
