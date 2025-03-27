from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
import random

app = FastAPI()

SECRET_KEY = "mysecret"

app.mount("/picture", StaticFiles(directory="picture"), name="picture")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://darknotfound404.web.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
prefixes = ['ผู้พิชิต', 'เทพเจ้า', 'จอมเวท', 'นักล่า', 'ราชันย์', 'จักรพรรดิ', 'นักฆ่า', 'เจ้าแห่ง', 'มหาเทพ', 'เจ้าชาย']
middles = ['หมัดเมา', 'มาม่าจานสุดท้าย', 'หมึกทอด', 'ไข่ตุ๋น', 'สามช่า', 'ไข่ดาว', 'ไวไฟหลุด', 'ข้าวมันไก่', 'หมูกรอบ', 'ข้าวขาหมู']
suffixes = ['ไร้เทียมทาน', 'ระดับจักรวาล', 'แห่งความว่างเปล่า', 'อมตะ', 'พันปี', 'ผู้ถูกลืม', 'แห่งดวงจันทร์ จะลงทัณฑ์แกเอง', 'สีรุ้ง', 'ตดไร้กลิ่น', 'แห่งมหานครนิวยอร์ก', 'ฟรุ้งฟริ้ง']

def verify_jwt(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/ifyouwantcoolname")
def generate_name(token_data: dict = Depends(verify_jwt)):
    name = f"{random.choice(prefixes)}{random.choice(middles)}{random.choice(suffixes)}"
    return {"nickname": name}

items_data = [
    {
        "id": 1,
        "category": "Product",
        "title": "Gun",
        "price": 27,
        "old_price": 52,
        "description": "promotion!! เทศกาลสงกรานต์!",
        "image": "/picture/1.jpg"
    },
    {
        "id": 2,
        "category": "Service",
        "title": "Hacker",
        "price": 82,
        "old_price": None,
        "description": "ผลงานเคยแก้รหัสเฟสให้ยาย",
        "image": "/picture/2.jpg"
    },
    {
        "id": 3,
        "category": "Clip",
        "title": "Funny Cat",
        "price": 99,
        "old_price": None,
        "description": "คลิปหลุดแมวอาบน้ำสระผม",
        "image": "/picture/3.jpg"
    },
    {
        "id": 4,
        "category": "Product",
        "title": "Fake Cat Citizen Card",
        "price": 30,
        "old_price": None,
        "description": "บัตรประชาชนแมวผู้ใหญ่อายุ2ขวบ",
        "image": "/picture/4.jpg"
    },
    {
        "id": 5,
        "category": "Service",
        "title": "สายลับจิ้งจก",
        "price": 27,
        "old_price": None,
        "description": "แอบฟังได้ทุกผนัง (ต้องขอความสมัครใจจากจิ้งจกก่อน)",
        "image": "/picture/5.jpg"
    },
    {
        "id": 6,
        "category": "Product",
        "title": "กางเกงพิสูจน์รักแท้",
        "price": 0.99,
        "old_price": 1,
        "description": None,
        "image": "/picture/6.jpg"
    },
    {
        "id": 7,
        "category": "Service",
        "title": "รถแห่แก้แค้นเพื่อนบ้าน",
        "price": 46,
        "old_price": None,
        "description": "ส่งรถแห่เข้าซอยเพื่อนบ้านที่เสียงดัง วันละ5ครั้ง",
        "image": "/picture/7.jpg"
    },
    {
        "id": 8,
        "category": "Service",
        "title": "Money Laundering",
        "price": 1,
        "old_price": None,
        "description": "บริการล้างเงินที่เลอะฝุ่น",
        "image": "/picture/8.jpg"
    },
    {
        "id": 9,
        "category": "Product",
        "title": "ยาเพิ่มพลัง",
        "price": 79,
        "old_price": 999,
        "description": None,
        "image": "/picture/9.jpg"
    },
    {
        "id": 10,
        "category": "Product",
        "title": "Dirty Money",
        "price": 0.01,
        "old_price": None,
        "description": "เงินเลอะอุนจิ" ,
        "image": "/picture/10.jpg"
    },
    {
        "id": 11,
        "category": "Service",
        "title": "แก๊งมาเฟียรับจ้าง",
        "price": 100,
        "old_price": None,
        "description": "รับข่วนทุกเบาะ เหมาะกับทุกโซฟา" ,
        "image": "/picture/11.jpg"
    },
    {
        "id": 12,
        "category": "Service",
        "title": "นักฆ่า(ยุง)",
        "price": 12,
        "old_price": None,
        "description": None,
        "image": "/picture/12.jpg"
    },
    {
        "id": 13,
        "category": "Service",
        "title": "บริการสะกดรอย",
        "price": 3,
        "old_price": None,
        "description": "กด follow ไอจีเป้าหมาย" ,
        "image": "/picture/13.jpg"
    },
    {
        "id": 14,
        "category": "Product",
        "title": "เหรียญ dog coin",
        "price": 0.01,
        "old_price": None,
        "description": None ,
        "image": "/picture/14.jpg"
    }
]

@app.get("/items")
def get_items(token_data: dict = Depends(verify_jwt)):
    return items_data