# app/main.py (بخش /chat را با این نسخه هماهنگ کن)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Literal
from app.db import search_base_products_by_text, top_sellers_for_base, get_con

app = FastAPI(title="My REST API + Torob Chat", version="1.2.0")

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
    type: Literal["text", "image"]
    content: str

class ChatRequest(BaseModel):
    chat_id: str
    messages: List[Message]

class ChatResponse(BaseModel):
    message: Optional[str] = None
    base_random_keys: Optional[List[str]] = None
    member_random_keys: Optional[List[str]] = None

@app.on_event("startup")
def startup():
    # warmup DB
    get_con()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(400, "messages cannot be empty")

    last = req.messages[-1]
    if last.type != "text":
        return ChatResponse(message="تصویر دریافت شد؛ لطفاً توضیح متنی هم بفرستید.")

    t = last.content.strip()
    tl = t.lower()

    # سناریوی صفر (همان‌طور که قبلاً پاس کردی)
    if tl == "ping":
        return ChatResponse(message="pong")
    if tl.startswith("return base random key:"):
        key = t.split(":", 1)[1].strip()
        return ChatResponse(base_random_keys=[key])
    if tl.startswith("return member random key:"):
        key = t.split(":", 1)[1].strip()
        return ChatResponse(member_random_keys=[key])

    # --- MVP جستجو روی دیتاست ---
    # اگر کاربر نام محصول/برند را نوشت → base_random_keys
    rows = search_base_products_by_text(t, limit=10)
    if rows:
        base_keys = [rk for (rk, _, _, _, _) in rows][:10]
        return ChatResponse(
            message="این نتایج نزدیک به جستجوی شماست.",
            base_random_keys=base_keys,
            member_random_keys=None,
        )

    # fallback
    return ChatResponse(message="چیزی پیدا نشد؛ لطفاً نام دقیق‌تری بفرمایید یا برند/مدل را مشخص کنید.")
