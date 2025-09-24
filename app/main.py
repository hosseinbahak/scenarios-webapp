from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="My REST API", version="1.0.0")

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

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in DB:
        raise HTTPException(404, "Item not found")
    DB[item_id] = item
    return {"id": item_id, **item.model_dump()}

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in DB:
        raise HTTPException(404, "Item not found")
    del DB[item_id]
    return
