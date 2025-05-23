from pydantic import BaseModel, Field

# ------------------------------ Data models ------------------------------ #
class UserIn(BaseModel):
    full_name: str
    username: str
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str

class Item(BaseModel):
    id: str
    title: str
    kind: str  # "movie" or "book"
    genre: str
    author: str

class RatingIn(BaseModel):
    item_id: str
    rating: int = Field(ge=1, le=5)

class RatingOut(BaseModel):
    item_id: str
    rating: int

class Recommendation(BaseModel):
    item_id: str
    title: str
    kind: str
    predicted_score: float