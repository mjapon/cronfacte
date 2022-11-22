# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import register

log = logging.getLogger(__name__)

engine = create_engine('postgresql://postgres:postgres@localhost:5432/imprentadb')


def get_dbsession():
    Session = sessionmaker(bind=engine)
    DBSession = scoped_session(Session)
    register(DBSession)
    session = DBSession
    return session
