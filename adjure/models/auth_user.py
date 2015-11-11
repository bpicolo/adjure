# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.types import VARBINARY

from adjure.models.base import Base


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    secret = Column(VARBINARY(32))
    key_length = Column(Integer)
    key_valid_duration = Column(Integer)
