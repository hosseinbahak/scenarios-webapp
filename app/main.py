# app/main.py  (اگر فایل در ریشه است، نام‌های import/command را مطابق بساز)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Literal

app = FastAPI(title="My REST API + Torob Chat", version="1.1.0")

# ---------- موجودی قبلی (/items) ----------
class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

DB: Dict[int, Item] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items")
def list_items():
    return [{"id": k, **v.model_dump()} for k, v in DB.items()]

@app.post("/items", status_code=201)
def create_item(item: Item):
    new_id = max(DB.keys(), default=0) + 1
    DB[new_id] = item
    return {"id": new_id, **item.model_dump()}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = DB.get(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return {"id": item_id, **item.model_dump()}

# ---------- Chat API برای سناریوی صفر ----------
from typing import List, Optional, Literal

class Message(BaseModel):
    type: Literal["text","image"]
    content: str

class ChatRequest(BaseModel):
    chat_id: str
    messages: List[Message]

class ChatResponse(BaseModel):
    message: Optional[str] = None
    base_random_keys: Optional[List[str]] = None
    member_random_keys: Optional[List[str]] = None

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(400, "messages cannot be empty")
    last = req.messages[-1]
    if last.type == "text":
        t = last.content.strip()
        tl = t.lower()
        if tl == "ping":
            return ChatResponse(message="pong")
        if tl.startswith("return base random key:"):
            return ChatResponse(base_random_keys=[t.split(":",1)[1].strip()])
        if tl.startswith("return member random key:"):
            return ChatResponse(member_random_keys=[t.split(":",1)[1].strip()])
        return ChatResponse(message="دریافت شد؛ بفرمایید دنبال چه محصول/برندی هستید؟")
    return ChatResponse(message="تصویر دریافت شد؛ لطفاً توضیح متنی هم بفرستید.")