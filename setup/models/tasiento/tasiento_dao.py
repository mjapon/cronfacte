# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from setup.models.conf import BaseDao
from setup.utils import ctes, numeros

log = logging.getLogger(__name__)


class TAsientoDao(BaseDao):

    def get_detdoc_foredit(self, trn_codigo, dt_tipoitem, joinarts=True):
        joinartsql = 'a.art_codigo'
        if not joinarts:
            joinartsql = 'a.cta_codigo'

        sqlic_nombre = 'b.ic_nombre'
        if dt_tipoitem == ctes.DT_TIPO_ITEM_PAGO:
            sqlic_nombre = 'b.ic_alias as ic_nombre'

        sql = """
            select a.dt_codigo, a.trn_codigo, a.cta_codigo, a.art_codigo, a.per_codigo, a.pry_codigo, a.dt_cant, a.dt_precio, a.dt_debito,
            a.dt_preref, a.dt_decto, a.dt_valor, a.dt_dectogen, a.dt_tipoitem, a.dt_valdto, a.dt_valdtogen, a.dt_codsec, {icnombre},
            b.ic_clasecc, b.ic_code, dimp.dai_imp0, dimp.dai_impg, dimp.dai_ise, dimp.dai_ice, 
            der.dtpreiva as dt_precioiva, der.icdpgrabaiva as icdp_grabaiva, der.subt as subtotal, der.total, der.dtdectoin as dt_dectoin
            from tasidetalle a
            left join tasidetimp dimp on a.dt_codigo = dimp.dt_codigo
            join get_dataforedit_rowfact(a.dt_codigo) as der(dtcod integer, 
            dtcant numeric, 
            dtprecio numeric,
            dtpreref numeric,
            dtdecto numeric,
            dtdectogen numeric,
            daiimpg numeric,
             dtpreiva numeric,
             dtdectoin numeric,
             icdpgrabaiva boolean,
             subt numeric,
             ivaval numeric,
             total numeric) on der.dtcod = a.dt_codigo
            join titemconfig b on {joinart} = b.ic_id where dt_tipoitem = {dttipo} and trn_codigo = {trncod}
            order by a.dt_codigo
            """.format(joinart=joinartsql,
                       icnombre=sqlic_nombre,
                       dttipo=dt_tipoitem,
                       trncod=trn_codigo)

        tupla_desc = ('dt_codigo', 'trn_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant',
                      'dt_precio', 'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem',
                      'dt_valdto', 'dt_valdtogen', 'dt_codsec', 'ic_nombre', 'ic_clasecc', 'ic_code', 'dai_imp0',
                      'dai_impg', 'dai_ise', 'dai_ice', 'dt_precioiva', 'icdp_grabaiva', 'subtotal', 'total',
                      'dt_dectoin')

        detalles = self.all(sql, tupla_desc)

        return detalles

    def get_detalles_doc(self, trn_codigo, dt_tipoitem, joinarts=True):

        joinartsql = 'a.art_codigo'
        if not joinarts:
            joinartsql = 'a.cta_codigo'

        sqlic_nombre = 'b.ic_nombre'
        if dt_tipoitem == ctes.DT_TIPO_ITEM_PAGO:
            sqlic_nombre = """case when coalesce(b.ic_alias,'')='' then b.ic_nombre else b.ic_alias end as ic_nombre"""

        sql = """
                select a.dt_codigo, trn_codigo, cta_codigo, art_codigo, per_codigo, pry_codigo, dt_cant, dt_precio, dt_debito,
                dt_preref, dt_decto, dt_valor, dt_dectogen, dt_tipoitem, dt_valdto, dt_valdtogen, dt_codsec, {icnombre},
                b.ic_clasecc, b.ic_code, dimp.dai_imp0, dimp.dai_impg, dimp.dai_ise, dimp.dai_ice
                from tasidetalle a
                left join tasidetimp dimp on a.dt_codigo = dimp.dt_codigo
                join titemconfig b on {joinart} = b.ic_id where dt_tipoitem = {dttipo} and trn_codigo = {trncod}
                order by a.dt_codigo
                """.format(joinart=joinartsql,
                           icnombre=sqlic_nombre,
                           dttipo=dt_tipoitem,
                           trncod=trn_codigo)

        tupla_desc = ('dt_codigo', 'trn_codigo', 'cta_codigo', 'art_codigo', 'per_codigo', 'pry_codigo', 'dt_cant',
                      'dt_precio', 'dt_debito', 'dt_preref', 'dt_decto', 'dt_valor', 'dt_dectogen', 'dt_tipoitem',
                      'dt_valdto', 'dt_valdtogen', 'dt_codsec', 'ic_nombre', 'ic_clasecc', 'ic_code', 'dai_imp0',
                      'dai_impg', 'dai_ise', 'dai_ice')

        detalles = self.all(sql, tupla_desc)

        return detalles

    @staticmethod
    def calcular_totales(detalles):
        gsubtotal = 0.0
        gsubtotal12 = 0.0
        gsubtotal0 = 0.0
        giva = 0.0
        gdescuentos = 0.0
        gtotal = 0.0
        descglobal = 0.0

        for det in detalles:
            dt_cant = det['dt_cant']
            dai_impg = det['dai_impg']
            dt_decto = det['dt_decto']
            dt_decto_cant = dt_decto * dt_cant
            if det['dt_valdto'] >= 0.0:
                dt_decto_cant = dt_decto
            dt_dectogen = det['dt_dectogen']
            dt_precio = det['dt_precio']
            subtotal = dt_cant * dt_precio
            subtforiva = (dt_cant * dt_precio) - (dt_decto_cant + dt_dectogen)
            ivaval = 0.0
            dt_dectogeniva = dt_dectogen
            if dai_impg > 0:
                ivaval = numeros.get_valor_iva(subtforiva, dai_impg)
                gsubtotal12 += subtforiva
                dt_dectogeniva = numeros.sumar_iva(dt_dectogen, dai_impg)
            else:
                gsubtotal0 += subtotal

            ftotal = subtotal - (dt_decto_cant + dt_dectogen) + ivaval
            giva += ivaval
            gdescuentos += (dt_decto_cant + dt_dectogen)
            gtotal += ftotal
            gsubtotal += subtotal
            descglobal += dt_dectogeniva

        return {
            'subtotal': numeros.roundm2(gsubtotal),
            'subtotal12': numeros.roundm2(gsubtotal12),
            'subtotal0': numeros.roundm2(gsubtotal0),
            'iva': numeros.roundm2(giva),
            'descuentos': numeros.roundm2(gdescuentos),
            'total': numeros.roundm2(gtotal),
            'descglobalin': numeros.roundm2(descglobal),
            'descglobal': numeros.roundm2(descglobal)
        }



