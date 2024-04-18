from pydantic import BaseModel
from typing import Optional

class Sentiment(BaseModel):
    mediaId: int
    mediaType: str
    reviewText: str
    rating: float

class runModel(BaseModel):
    reviewText: str
    id:int
    mediaID:int