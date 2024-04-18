
from fastapi import APIRouter, Depends, FastAPI
from tmdbv3api import TMDb, Discover, Genre
from typing import Union,List, Dict
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import os
from database import conn
from schemas import Sentiment
from schemas import runModel
from sqlalchemy import update, select

from models import Sentiments
import pickle
from pathlib import Path
from sqlalchemy import update, select

auth = APIRouter()
app = FastAPI()

tmdb = TMDb()
tmdb.api_key = 'f81105d6df16781cf97141803a294d1c'
tmdb.language = 'en'
tmdb.debug = True


def sentiment_analysis(review_text: str, id: int, mediaID: int) -> Dict[str, any]:
    current_dir = os.getcwd()
    max_length = 100
    trunc_type = 'post'
    model_path = os.path.join(current_dir, "fast_api/sentiment.h5")
    tokenizer_path = os.path.join(current_dir, "fast_api/tokenizer.pickle")
    
    # Load model
    new_model = load_model(model_path)
    if new_model is None:
        return {"error": "Failed to load model."}
    
    # Load tokenizer
    with open(tokenizer_path, 'rb') as handle:
        tk = pickle.load(handle)
    if tk is None:
        return {"error": "Failed to load tokenizer."}
    
    # Tokenize and pad the review text
    review_texts = [review_text]
    new_sequences = tk.texts_to_sequences(review_texts)
    padded = pad_sequences(new_sequences, maxlen=max_length, truncating=trunc_type)
    
    # Predict sentiment
    prediction = new_model.predict(padded)[0]
    sentiment = "Positive" if prediction > 0.53 else "Negative"
    
    # Update database with sentiment score
    conn.execute(
        update(Sentiments)
        .where(Sentiments.c.id == id)
        .values(score=float(prediction),sentiment=sentiment)
    )
    
    # Retrieve all rows from the database where mediaId matches
    result = conn.execute(
        select([Sentiments])
        .where(Sentiments.c.mediaId == mediaID)
    ).fetchall()
    
    # Convert result to dictionary
    rows = [dict(row) for row in result]
    return rows
    

def get_tv_shows():
    discover = Discover()
    shows = discover.discover_tv_shows({
        'primary_release_date.gte': '1960-01-01',
    })
    genre = Genre()
    genre_list = genre.tv_list()
    genre_dict = {genre.id: genre.name for genre in genre_list}
    return [{'id': show.id,
             'name': show.name,
             'backdrop_path': show.backdrop_path,
              'poster_path': show.poster_path,
             'release_date': show.first_air_date,
             'genres': [genre_dict[genre_id] for genre_id in show.genre_ids],
             'origin_country': show.origin_country,
             'original_language': show.original_language,
             'overview': show.overview} for show in shows]


def get_movies() -> List[dict]:
    discover = Discover()
    movies = discover.discover_movies({
        'primary_release_date.gte': '2021-01-01',
        'primary_release_date.lte': '2024-04-02'
    })
    genre = Genre()
    genre_list = genre.movie_list()
    genre_dict = {genre.id: genre.name for genre in genre_list}
    return [{'id': movie.id,
             'title': movie.title,
             'backdrop_path': movie.backdrop_path,
               'poster_path': movie.poster_path,
             'release_date': movie.release_date,
             'genres': [genre_dict[genre_id] for genre_id in movie.genre_ids],
             'original_language': movie.original_language,
             'overview': movie.overview} for movie in movies]

@auth.get("/tv_shows/")
def read_tv_shows():
    return get_tv_shows()

@auth.post("/sentiment/")
def get_sentiment_analysis(req:runModel):
    return sentiment_analysis(req.reviewText,req.id,req.mediaID)

@auth.get("/movies/")
def read_movies():
    return get_movies()

@auth.post('/reviews')
def create_sentiment(req:Sentiment):
    conn.execute(Sentiments.insert().values(
	    mediaId = req.mediaId,
        mediaType = req.mediaType,
        rating = req.rating,
	    reviewText = req.reviewText
    ))
    return (conn.execute(Sentiments.select()).lastrowid)

@auth.get("/getreview/{mediaType}/{id}")
async def get_reviews(mediaType: str, id: int):
    return conn.execute(Sentiments.select().where((Sentiments.c.mediaId == id) & (Sentiments.c.mediaType == mediaType))).fetchall()


@auth.get("/getreviews/{mediaType}/{mid}")
async def get_review( id: int):
    return conn.execute(Sentiments.select().where( (Sentiments.c.mediaId == id) )).fetchall()


def get_tv_genres():
    genre = Genre()
    tv_genre_list = genre.tv_list()
    return [{'id': genre.id, 'name': genre.name} for genre in tv_genre_list]

def get_movie_genres():
    genre = Genre()
    movie_genre_list = genre.movie_list()
    return [{'id': genre.id, 'name': genre.name} for genre in movie_genre_list]

@auth.get("/tv_genres/")
def read_tv_genres():
    return get_tv_genres()

@auth.get("/movie_genres/")
def read_movie_genres():
    return get_movie_genres()



