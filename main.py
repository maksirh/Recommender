from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Dict, Optional
from uuid import uuid4
import random
import uvicorn
from models import *

app = FastAPI(title="Recommender")

users: Dict[str, dict] = {}
items: Dict[str, Item] = {}
ratings: Dict[str, List[RatingOut]] = {}  # key = user_id

def _seed_items():
    sample_items = [
        ("The Lord of the Rings", "book", "fantasy", "J.R.R. Tolkien"),
        ("Dune", "book", "sci‑fi", "Frank Herbert"),
        ("Interstellar", "movie", "sci‑fi", "Christopher Nolan"),
        ("Inception", "movie", "thriller", "Christopher Nolan"),
        ("Pride and Prejudice", "book", "romance", "Jane Austen"),
        ("La La Land", "movie", "musical", "Damien Chazelle"),
    ]
    for title, kind, genre, author in sample_items:
        item_id = str(uuid4())
        items[item_id] = Item(id=item_id, title=title, kind=kind, genre=genre, author=author)

_seed_items()

def authenticate(email: str, password: str) -> dict:
    for u in users.values():
        if u["email"] == email and u["password"] == password:
            return u
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


def get_current_user(token: str = ""):
    # Very primitive "auth": we expect ?token=<user_id>
    if token and token in users:
        return users[token]
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or bad token")


@app.post("/register", response_model=UserOut)
def register(user_in: UserIn):
    if any(u["email"] == user_in.email for u in users.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid4())
    user = user_in.dict()
    user.update({"id": user_id})
    users[user_id] = user
    ratings[user_id] = []
    return UserOut(id=user_id, username=user_in.username)

@app.post("/login")
def login(creds: LoginIn):
    user = authenticate(creds.email, creds.password)
    return {"token": user["id"], "username": user["username"]}

@app.get("/items", response_model=List[Item])
def list_items():
    return list(items.values())

@app.post("/rate", response_model=RatingOut)
def rate(rating_in: RatingIn, user=Depends(get_current_user)):
    if rating_in.item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    r = RatingOut(item_id=rating_in.item_id, rating=rating_in.rating)
    # Replace if exists
    user_ratings = ratings[user["id"]]
    existing = next((x for x in user_ratings if x.item_id == r.item_id), None)
    if existing:
        user_ratings.remove(existing)
    user_ratings.append(r)
    return r

@app.get("/recommendations", response_model=List[Recommendation])
def recommend(user=Depends(get_current_user)):
    user_ratings = ratings.get(user["id"], [])
    if user_ratings:
        top_item = max(user_ratings, key=lambda x: x.rating)
        top_genre = items[top_item.item_id].genre
        candidate_items = [i for i in items.values() if i.genre == top_genre and i.id != top_item.item_id]
    else:
        candidate_items = list(items.values())
    random.shuffle(candidate_items)
    recs = candidate_items[:5]
    return [
        Recommendation(item_id=i.id, title=i.title, kind=i.kind, predicted_score=random.uniform(3, 5))
        for i in recs
    ]

@app.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return UserOut(id=user["id"], username=user["username"])

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)