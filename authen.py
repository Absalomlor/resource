from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ต้อง import ให้ถูกต้อง
from pydantic import BaseModel
from jose import jwt
import datetime

app = FastAPI()

# ใส่ URL ต้นทางของเราให้ถูกต้อง
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://darknotfound404.web.app"],  # หรือ ["*"] ชั่วคราวเพื่อทดสอบ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "mysecret"

class AuthRequest(BaseModel):
    client_id: str
    client_secret: str

db = {
    "client_id": "client0",
    "client_secret": "thisissecret"
}

def create_jwt_token(data: dict, expires_delta: int):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

@app.post("/auth")
def authenticate(auth: AuthRequest):
    if auth.client_id == db["client_id"] and auth.client_secret == db["client_secret"]:
        token = create_jwt_token({"sub": auth.client_id}, expires_delta=1)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")