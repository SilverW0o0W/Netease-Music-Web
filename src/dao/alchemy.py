#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# class Database(object):
#     def __init__(self, connect_string):
#         self.engine = create_engine(connect_string)
#
#     def connect(self):
#         return sessionmaker(bind=self.engine)


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    origin_id = Column(String(20))
    name = Column(String(100))
    artists = Column(String(100))
    created_time = Column(Integer)
    updated_time = Column(Integer)


def session_watcher(commit):
    def _session_watcher(func):
        def wrapper(self, *args, **kwargs):
            # If the args contain session, the session will not close.
            has_connected = 'session' in kwargs and kwargs['session']
            if has_connected:
                session = kwargs['session']
            else:
                session = self.session()
                kwargs['session'] = session
            try:
                result = func(self, *args, **kwargs)
            except Exception as ex:
                raise ex
            else:
                if commit:
                    session.commit()
                return result
            finally:
                if not has_connected:
                    session.close()

        return wrapper

    return _session_watcher


class DBWorker(object):
    def __init__(self, con_string):
        self.con_string = con_string
        self.engine = None
        self.Session = None
        self.create_table()

    def session(self):
        if not self.engine:
            self.engine = create_engine(self.con_string, connect_args={'check_same_thread': False})
            self.Session = sessionmaker(bind=self.engine)
        return self.Session()

    def create_table(self):
        engine = create_engine(self.con_string)
        Base.metadata.create_all(engine)
        engine.dispose()

    @session_watcher(True)
    def merge_song(self, song, session=None):
        session.add(song)

    @session_watcher(False)
    def query_song(self, song_id, session=None):
        return session.query(Song).filter_by(origin_id=song_id).one_or_none()
