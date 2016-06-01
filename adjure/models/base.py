# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
session = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def bind_database_engine(connection_string):
    engine = create_engine(connection_string, convert_unicode=True)
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    return engine
