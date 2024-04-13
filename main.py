from pydantic import BaseModel, Field
from config import CONFIG
from app import app
from db import get_db
from fastapi import Depends, WebSocket, Request
from typing import Annotated, Any
import resend
import secrets
import uvicorn
from pymongo import MongoClient
from pymongo.database import Database
from mail import make_link_msg, send_conf_mail_to

class Card(BaseModel):
    id: str | None = Field(alias="_id", exclude=True, default=None)
    title: str
    description: str
    column: str
    
    class Config:
        orm_mode = True

@app.post("/insert")
def insert_card(card: Card, db: MongoClient = Depends(get_db)):
        
    post_id = db.fastapp.cards.insert_one(card.model_dump()).inserted_id
    return {"cid": str(post_id)}


@app.get("/cards")
def test(db: MongoClient = Depends(get_db)):
    cards = []
    for card in db.fastapp.cards.find():
        card["_id"] = str(card["_id"])
        cards.append(card)
    return {"cards": cards}


class LoginUser(BaseModel):
    email: str

    class Config:
        orm_mode = True

@app.post("/login")
def login(request: Request, link_format: str, user: LoginUser):
    random_bytes = secrets.token_bytes(16)
    token = random_bytes.hex()
    session_mgr = request.state.session
    session = session_mgr.get_session()
    session["token"] = token
    session["username"] = user.email.split("@")[0]


    msg = make_link_msg(link_format, token)
    sent = send_conf_mail_to(user.email, msg)
    return {"success": sent}


@app.get("/user")
def user(request: Request, key: str):
    session_mgr = request.state.session
    session = session_mgr.get_session()
    token = session.get("token", None)
    if token is not None:
        if token == key:
            return {"success": True, "username": session["username"]}
    if token is not None:
        del session["token"]
    if session.get("username", None) is not None:
        del session["username"]
    return {"success": False, "username": None}

@app.websocket("/watch")
def watch_changes(websocket: WebSocket, db: MongoClient = Depends(get_db)):
    websocket.accept()
    while True:
        data = db.fastapp.cards.watch()
        websocket.send(data)


if __name__ == "__main__":
    uvicorn.run(app="app:app", reload=CONFIG.DEBUG)
