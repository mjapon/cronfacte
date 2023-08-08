# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from setup.models.conf import BaseDao

log = logging.getLogger(__name__)


class TComprobanteDao(BaseDao):

    def existe_clave_acceso(self, claveacceso):
        sql = """
        select count(*) as cuenta from comprobantes.tcomprobante where cmp_claveaccesso = '{0}'
        """.format(claveacceso)

        cuenta = self.first_col(sql, 'cuenta')
        return cuenta > 0

    def crear(self, form):
        """
        if not self.existe_clave_acceso(claveacceso=form['cmp_claveaccesso']):
            tcomprobante = TComprobante()
            tcomprobante.cmp_tipo = form['cmp_tipo']
            tcomprobante.cmp_numero = form['cmp_numero']
            tcomprobante.cmp_trncod = form['cmp_trncod']
            tcomprobante.cmp_claveaccesso = form['cmp_claveaccesso']
            tcomprobante.cnt_id = form['cnt_id']
            tcomprobante.emp_codigo = form['emp_codigo']
            tcomprobante.cmp_fecha = fechas.parse_cadena(form['cmp_fecha'])
            tcomprobante.cmp_total = form['cmp_total']

            self.dbsession.add(tcomprobante)
        """
