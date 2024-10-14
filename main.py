from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()


def init_db():
    conn = sqlite3.connect('example.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL
    )''')
    conn.close()


@app.on_event("startup")
def startup():
    init_db()

class Item(BaseModel):
    name: str
    description: str
    price: float = 0.0

# Create an Item
@app.post('/items/')
def create_new_item(item: Item):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, description, price) VALUES (?, ? , ?)",
                   (item.name, item.description, item.price)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return {"id": item_id, "name": item.name, "description": item.description, "price": item.price}


@app.get('/items/')
def read_items():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return {"items": items}

@app.get('/items/{item_id}')
def read_item(item_id: int):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail='Item Not Found')
    return {"id": item[0], "name": item[1], "description": item[2], "price": item[3]}

@app.put('/items/{item_id}')
def update_item(item_id: int, name: str, description: str, price: float):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name=?, description=?, price=? WHERE id=?",
                   (name, description, price, item_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Item Updated"}


@app.patch('/items/{item_id}')
def partial_update_item(item_id: int, name: str):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name=? WHERE id=?",
                   (name, item_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Item Partially Updated"}

@app.delete('/items/{item_id}')
def delete_item(item_id: int):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item Deleted"}


