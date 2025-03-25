from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
import random
 
app = FastAPI()
SECRET_KEY = "mysecret"
 
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
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
 
@app.get("/ifyouwantcoolname")
def generate_name(token_data: dict = Depends(verify_jwt)):
    name = f'ชื่อของท่านคือ "{random.choice(prefixes)}{random.choice(middles)}{random.choice(suffixes)}"'
    return {"nickname": name}