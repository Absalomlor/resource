import os
import jwt
import hashlib
import pandas as pd
import chromadb
from loguru import logger
from chromadb.utils import embedding_functions
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pythainlp.tokenize import subword_tokenize, syllable_tokenize
from sentence_transformers import SentenceTransformer, util

# Env
os.environ["PYTHAINLP_DATA_DIR"] = "/app/pythainlp-data"
os.environ["HF_HOME"] = "/app/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/app/huggingface"
os.environ["HF_HUB_CACHE"] = "/app/huggingface"

# Log Directory
LOG_DIR = "/tmp/logs"
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(f"{LOG_DIR}/logging_file.log", format="{time} {level} {message}", rotation="500 MB")

# JWT และ Authentication
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# แฮชรหัสผ่านด้วย SHA256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ตรวจสอบรหัสผ่าน
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# ฐานข้อมูลผู้ใช้
fake_users_db = {
    "admin": hash_password("admin123"),
    "user": hash_password("user123")
}

# ตรวจสอบผู้ใช้
def authenticate_user(username: str, password: str):
    user_hashed_password = fake_users_db.get(username)
    if not user_hashed_password or not verify_password(password, user_hashed_password):
        return None
    return {"username": username}

# สร้าง JWT Token
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ตรวจสอบ JWT Token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token ไม่ถูกต้อง")

# โหลดข้อมูลจาก Excel
df = pd.read_excel('manga_clean.xlsx')
documents = df['Description'].tolist()
manga_ids = df.index.to_list()
manga_names = df['Character'].tolist()

# Model สำหรับ Embedding
EMBED_MODEL = "paraphrase-multilingual-mpnet-base-v2"
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBED_MODEL,
    device="cpu",
    normalize_embeddings=True,
)

# ChromaDB
DB_PATH = "/tmp/chroma_db"
os.makedirs(DB_PATH, exist_ok=True)
client = chromadb.PersistentClient(path=DB_PATH)
COLLECTION_NAME = "manga_docs"
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_func,
    metadata={"hnsw:space": "l2"},
)

# เพิ่มข้อมูลลงใน ChromaDB
collection.add(
    documents=documents,
    ids=[str(i) for i in manga_ids],
    metadatas=[{"name": manga_names[n]} for n in range(len(df))]
)

# Sentence Transformer Model
model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')

# ค้นหาตัวละครที่เกี่ยวข้อง
def get_related_character(query, alpha=1):
    result = {'ids': [[]]}

    # 🔹 Tokenization
    tokens = [t.replace("▁", "") for t in subword_tokenize(query, engine='wangchanberta') if len(t) > 1]
    tokens = [t for t in tokens if t not in ["เป็น", "มี", "ว่า", "ชอบ", "แล้ว", "กับ"]]

    # 🔹 Query ChromaDB
    if len(tokens) > 1:
        result = collection.query(
            query_texts=query,
            where_document={"$or": [{"$contains": i} for i in tokens]},
            n_results=10
        )
    elif len(tokens) == 1:
        result = collection.query(
            query_texts=query,
            where_document={"$contains": query},
            n_results=10
        )

    # 🔹 ถ้าไม่มีผลลัพธ์ ให้ใช้ Semantic Search
    if len(result.get('ids')[0]) == 0:
        result = collection.query(query_texts=query, n_results=20)

    # 🔹 คำนวณคะแนน Reranking
    query_texts = [f'Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: {query}']
    query_embeddings = model.encode(query_texts, normalize_embeddings=True)
    doc_texts = [doc.strip() for doc in result['documents'][0]]
    doc_embeddings = model.encode(doc_texts, normalize_embeddings=True)
    rerank_score = util.cos_sim(query_embeddings, doc_embeddings)[0].numpy()

    # 🔹 แพ็คข้อมูลที่ได้
    df_result = pd.DataFrame({
        "name": [meta['name'] for meta in result['metadatas'][0]],
        "passage": doc_texts,
        "sim_score": [1 - dis for dis in result['distances'][0]],
        "rerank_score": rerank_score
    })
    df_result["weight_score"] = df_result["sim_score"] * (1 - alpha) + df_result["rerank_score"] * alpha
    df_result = df_result.sort_values(by="weight_score", ascending=False).head(5)

    return df_result.to_dict()

# FastAPI
app = FastAPI()

# ค้นหาข้อมูล
@app.post('/retrival')
async def query(data: dict = Body()):
    query = data.get("query")
    result = get_related_character(query)
    return result

# ดึงข้อมูลทั้งหมด
@app.get('/all')
async def all_doc():
    result = collection.get()
    return result

# เพิ่มข้อมูลใหม่
@app.post('/add')
async def add_document(data: dict = Body()):
    try:
        new_documents = data.get("documents", [])
        new_ids = data.get("ids", [])
        new_metas = data.get("metadatas", [])

        if len(new_documents) != len(new_ids) or len(new_ids) != len(new_metas):
            return {"error": "documents, ids และ metadatas ต้องมีจำนวนเท่ากัน"}

        collection.add(documents=new_documents, ids=new_ids, metadatas=new_metas)
        return {"message": "เพิ่มข้อมูลสำเร็จ", "count": len(new_documents)}
    except Exception as e:
        return {"error": str(e)}

# Authentication
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ตรวจสอบ JWT Token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token ไม่ถูกต้อง")
    return username

# Protected Route (Authorization)
@app.get("/protected")
async def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello {user}, คุณเข้าถึงข้อมูลนี้ได้!"}
