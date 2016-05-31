# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.types import VARBINARY

from adjure.models.base import Base


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    secret = Column(VARBINARY(32), nullable=False)
    key_length = Column(Integer, nullable=False)
    key_valid_duration = Column(Integer, nullable=False)
    hash_algorithm = Column(String(8), nullable=False)
