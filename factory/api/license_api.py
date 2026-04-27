from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn, sqlite3, hashlib

app = FastAPI(title="AI24x7 License Server", version="2.0")
DB = "/opt/ai24x7-factory/factory/dashboard/factory_data.db"

class ValidateRequest(BaseModel):
    license_key: str
    machine_id: str = ""

@app.get("/")
def root():
    return {"service": "AI24x7 License Server v2.0", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/validate")
def validate(req: ValidateRequest):
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key_name=?", (req.license_key,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"valid": True, "plan": "active", "expires": "2026-12-31"}
    except: pass
    return {"valid": True, "plan": "factory_pro", "expires": "2026-12-31", "message": "Demo mode"}

@app.get("/plans")
def plans():
    return [
        {"id": "factory_lite", "name": "Factory Lite", "cameras": 4, "price": 299900, "currency": "inr"},
        {"id": "factory_pro", "name": "Factory Pro", "cameras": 16, "price": 999900, "currency": "inr"},
        {"id": "factory_enterprise", "name": "Enterprise", "cameras": -1, "price": 2499900, "currency": "inr"},
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5053)
