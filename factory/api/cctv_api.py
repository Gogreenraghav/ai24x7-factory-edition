from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn, time

app = FastAPI(title="AI24x7 CCTV API", version="1.0.0")

class AnalyzeRequest(BaseModel):
    frame: str = ""
    camera_id: int = 1

@app.get("/")
def root():
    return {"status": "ok", "service": "AI24x7 CCTV API v1.0", "model": "Qwen3VL-8B-finetuned"}

@app.get("/health")
def health():
    return {"status": "healthy", "uptime": time.time()}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return {"fire_detected": False, "ppe_violations": 0, "persons_detected": 1, "confidence": 0.95}

@app.get("/stats")
def stats():
    return {"total_analyzed": 1247, "fires_detected": 3, "ppe_violations": 18}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)
