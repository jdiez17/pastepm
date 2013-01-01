from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from pastepm.database import Base, using_redis, r
from pastepm.config import config

import hashlib

class Paste(Base):
    __tablename__ = 'pastes'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Paste id %d: "%s">' % (self.id, self.content)

    def __str__(self):
        return self.content

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    pwdhash = Column(String(40))
    activated = Column(Boolean)

    @staticmethod
    def _get_hash(plain):
        h = hashlib.sha1()
        h.update(plain)

        return h.hexdigest()

    def __init__(self, username, password, payment_enabled=False):
        self.username = username
        self.pwdhash = self._get_hash(password) 
        self.activated = not payment_enabled
       
    def check_password(self, password):
        return self._get_hash(password) == self.pwdhash

