from sqlalchemy import create_engine, Column, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Word(Base):
    __tablename__ = 'words'
    word = Column(String(5), primary_key=True)
    is_daily = Column(Boolean, default=False)
    added_date = Column(Date, default=datetime.now())

class Game(Base):
    __tablename__ = 'games'
    user_id = Column(String(20), primary_key=True)
    target_word = Column(String(5))
    attempts = Column(String(255))
    remaining_guesses = Column(String(30))

engine = create_engine('sqlite:///wordle.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
