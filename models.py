from sqlalchemy import Table, Column, MetaData, Float, Integer, String, DateTime
from sqlalchemy import func  # Correct import statement for func
from database import engine
from datetime import datetime

meta = MetaData()

Sentiments = Table('Sentiments', meta,
    Column('id', Integer, primary_key=True),
    Column('mediaId', Integer),
    Column('mediaType', String),
    Column('reviewText', String),
    Column('sentiment', String),
    Column('score', Float),
    Column('rating', Float))

meta.create_all(engine)
