from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="AI24x7 Payment Server", version="1.0")

class CheckoutRequest(BaseModel):
    plan_id: str
    name: str
    email: str
    phone: str
    factory_name: str

@app.get("/")
def root():
    return {"service": "AI24x7 Payment Server v1.0", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/plans")
def plans():
    return [
        {"id": "factory_lite", "name": "Factory Lite", "cameras": 4, "price": 299900},
        {"id": "factory_pro", "name": "Factory Pro", "cameras": 16, "price": 999900},
        {"id": "factory_enterprise", "name": "Enterprise", "cameras": -1, "price": 2499900},
    ]

@app.post("/create-checkout")
def create_checkout(req: CheckoutRequest):
    return {"url": "http://43.242.224.231:5055", "message": "Stripe checkout (configure with live keys)"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5055)
