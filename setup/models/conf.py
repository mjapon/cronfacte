# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

import transaction
from sqlalchemy import text
from sqlalchemy.ext.declarative import as_declarative

from setup.utils.jsonutil import SimpleJsonUtil

log = logging.getLogger(__name__)


@as_declarative()
class Declarative(object):
    pass


class BaseDao(SimpleJsonUtil):

    def __init__(self, dbsession, default_schema=""):
        self.dbsession = dbsession
        self.default_schema = default_schema

    def set_default_shema(self):
        self.set_esquema(self.default_schema)

    def set_esquema(self, esquema):
        self.dbsession.execute("SET search_path TO {0}".format(esquema))

    def all(self, sql, tupla_desc):
        res = self.dbsession.query(*tupla_desc).from_statement(text(sql)).all()
        return self.make_json_list(res, tupla_desc)

    def first(self, sql, tupla_desc):
        tupla_res = self.dbsession.query(*tupla_desc).from_statement(text(sql)).first()
        return None if tupla_res is None else self.tupla_to_json(tupla_res, tupla_desc)

    def first_col(self, sql, col):
        tupla_res = self.dbsession.query(col).from_statement(text(sql)).first()
        return tupla_res[0] if tupla_res is not None and tupla_res[0] is not None else None

    def flush(self):
        self.dbsession.flush()

    def commit(self):
        self.dbsession.commit()
        # transaction.commit()
