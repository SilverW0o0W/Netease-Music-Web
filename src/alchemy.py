# coding=utf-8
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    origin_id = Column(String(20))
    name = Column(String(100))
    artists = Column(String(100))
    created_time = Column(Integer)
    updated_time = Column(Integer)
