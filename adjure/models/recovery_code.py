# -*- coding: utf-8 -*-
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from adjure.models.base import Base


class RecoveryCode(Base):
    __tablename__ = 'adjure_recovery_code'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        String(128),
        ForeignKey('adjure_auth_user.user_id'),
        nullable=False,
    )
    code = Column(String(32), unique=False, nullable=False, index=True)
    used = Column(Boolean, nullable=False, default=False)
