# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from setup.models.conf import BaseDao
from setup.models.tcontribuyente.tcontribuyente_model import TContribuyente
from setup.utils import cadenas

log = logging.getLogger(__name__)


class TContribuyenteDao(BaseDao):

    def existe_ciruc(self, per_ciruc):
        sql = """
        select count(*) as cuenta from comprobantes.tcontribuyente where cnt_ciruc = '{0}'
        """.format(cadenas.strip(per_ciruc))

        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def find_by_cnt_ciruc(self, cnt_ciruc):
        return self.dbsession.query(TContribuyente).filter(TContribuyente.cnt_ciruc == cadenas.strip(cnt_ciruc)).first()

    def crear(self, form):
        tcontribuyente = TContribuyente()
        tcontribuyente.cnt_ciruc = cadenas.strip(form['cnt_ciruc'])
        tcontribuyente.cnt_nombres = cadenas.strip_upper(form['cnt_nombres'])
        cnt_apellidos = None
        if cadenas.es_nonulo_novacio(form['cnt_apellidos']):
            cnt_apellidos = cadenas.strip_upper(form['cnt_apellidos'])

        tcontribuyente.cnt_apellidos = cnt_apellidos
        tcontribuyente.cnt_direccion = cadenas.strip(form['cnt_direccion'])
        tcontribuyente.cnt_telf = cadenas.strip(form['cnt_telf'])
        tcontribuyente.cnt_email = cadenas.strip(form['cnt_email'])
        tcontribuyente.cnt_movil = cadenas.strip(form['cnt_movil'])
        tcontribuyente.cnt_estado = 0
        tcontribuyente.cnt_clave = cadenas.strip(form['cnt_ciruc'])
        tcontribuyente.cnt_estado_clave = 0

        self.dbsession.add(tcontribuyente)

    def actualizar(self, form):
        tcontribuyente = self.find_by_cnt_ciruc(cnt_ciruc=form['cnt_ciruc'])
        if tcontribuyente is not None:
            tcontribuyente.cnt_nombres = cadenas.strip_upper(form['cnt_nombres'])
            cnt_apellidos = None
            if cadenas.es_nonulo_novacio(form['cnt_apellidos']):
                cnt_apellidos = cadenas.strip_upper(form['cnt_apellidos'])

            tcontribuyente.cnt_apellidos = cnt_apellidos
            tcontribuyente.cnt_direccion = cadenas.strip(form['cnt_direccion'])
            tcontribuyente.cnt_telf = cadenas.strip(form['cnt_telf'])
            tcontribuyente.cnt_email = cadenas.strip(form['cnt_email'])
            tcontribuyente.cnt_movil = cadenas.strip(form['cnt_movil'])
            self.dbsession.add(tcontribuyente)

    def create_or_update(self, form):
        tcontribuyente = self.find_by_cnt_ciruc(cnt_ciruc=form['cnt_ciruc'])
        if tcontribuyente is not None:
            self.actualizar(form)
        else:
            self.crear(form)

        self.dbsession.flush()

        tcontribuyente = self.find_by_cnt_ciruc(cnt_ciruc=form['cnt_ciruc'])
        return tcontribuyente.cnt_id
