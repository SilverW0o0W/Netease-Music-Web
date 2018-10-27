#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Database(object):
    def __init__(self, connect_string):
        self.engine = create_engine(connect_string)

    def connect(self):
        return sessionmaker(bind=self.engine)


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    origin_id = Column(String(20))
    name = Column(String(100))
    artists = Column(String(100))
    created_time = Column(Integer)
    updated_time = Column(Integer)
