# -*- coding: utf-8 -*-
import staticconf

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    staticconf.NamespaceReaders('adjure').read('database.connection_string'),
    convert_unicode=True,
)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()
