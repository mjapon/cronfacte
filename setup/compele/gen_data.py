# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from setup.models.conf import BaseDao
from setup.models.tasiento.tasiento_dao import TAsientoDao
from setup.models.tasifacte.tasifacte_dao import TasiFacteDao
from setup.utils import fechas, ctes_facte, ctes

log = logging.getLogger(__name__)


class GenDataForFacte(BaseDao):

    def get_data_for_save_conbrib(self, trn_codigo):
        datos_fact = self.get_factura_data(trn_codigo=trn_codigo)
        clave_acceso = self.get_clave_acceso(datos_factura=datos_fact['cabecera'])


    def get_clave_acceso(self, datos_factura, tipo_ambiente):
        trn_fecreg = datos_factura['trn_fecreg']

        fechafact = fechas.format_cadena(trn_fecreg, ctes.APP_FMT_FECHA, ctes_facte.APP_FMT_FECHA_SRI)
        tipo_comprobante = '01'
        num_ruc = datos_factura['alm_ruc']

        # serie = '{0}{1}'.format(datos_factura['alm_numest'], datos_factura['tdv_numero'])

        trn_compro = datos_factura['trn_compro']
        serie_secuencial = trn_compro

        codigo_numerico = "00000000"  # potestad del contribuyente

        tipo_emision = "1"

        pre_clave_acceso = "{0}{1}{2}{3}{4}{5}{6}".format(fechafact, tipo_comprobante, num_ruc, tipo_ambiente,
                                                          serie_secuencial, codigo_numerico, tipo_emision)

        digito = self.get_digito_verificador(pre_clave_acceso)

        clave_acceso = '{0}{1}'.format(pre_clave_acceso, digito)
        return clave_acceso

    def get_factura_data(self, trn_codigo):
        sql = """
        select 
                asi.trn_fecreg,
                talm.alm_ruc,
                asi.trn_compro,
                talm.alm_razsoc,
                talm.alm_nomcomercial,
                talm.alm_numest,
                ttpdv.tdv_numero,
                talm.alm_direcc,
                asi.per_codigo,
                per.per_ciruc,
                0 as propina,
                per.per_nombres||' '||coalesce(per.per_apellidos,'') per_nomapel,
                per.per_direccion from tasiento asi
                join ttpdv on asi.tdv_codigo =   ttpdv.tdv_codigo
                join talmacen talm on ttpdv.alm_codigo = talm.alm_codigo
                join tpersona per on asi.per_codigo = per.per_id
                where asi.trn_codigo = {0}        
        """.format(trn_codigo)

        tupla_desc = ('trn_fecreg',
                      'alm_ruc',
                      'trn_compro',
                      'alm_razsoc',
                      'alm_nomcomercial',
                      'alm_numest',
                      'tdv_numero',
                      'alm_direcc',
                      'per_codigo',
                      'per_ciruc',
                      'propina',
                      'per_nomapel',
                      'per_direccion')

        datos_factura = self.first(sql, tupla_desc)

        tasidao = TAsientoDao(self.dbsession)
        detalles = tasidao.get_detdoc_foredit(trn_codigo=trn_codigo, dt_tipoitem=1)
        pagos = tasidao.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=2, joinarts=False)
        totales = tasidao.calcular_totales(detalles)

        totales_facte = {
            'total_sin_impuesto': totales['subtotal'],
            'total_descuentos': totales['descuentos'],
            'base_imp_iva_12': totales['subtotal12'],
            'impuesto_iva_12': totales['iva'],
            'total': totales['total'],
            'pago_efectivo': totales['total'],
            'pago_credito': 0,  # TODO:
        }

        return {'cabecera': datos_factura,
                'detalles': detalles,
                'pagos': pagos,
                'totales': totales_facte}

    def save_proxy_send_response(self, trn_codigo, ambiente, proxy_response):
        tasifacte_dao = TasiFacteDao(self.dbsession)
        if proxy_response['claveAcceso'] is not None:
            data = {
                'tfe_estado': proxy_response['estado'],
                'tfe_estadosri': proxy_response['estadoSRI'],
                'tfe_fecautoriza': proxy_response['fechaAutorizacion'] if 'fechaAutorizacion' in proxy_response else '',
                'tfe_mensajes': str(proxy_response['mensajes']) if 'mensajes' in proxy_response else '',
                'tfe_numautoriza': proxy_response[
                    'numeroAutorizacion'] if 'numeroAutorizacion' in proxy_response else '',
                'tfe_ambiente': ambiente,
                'tfe_claveacceso': proxy_response['claveAcceso']
            }

            tasifacte_dao.create_or_update(trn_codigo=trn_codigo, data=data)
            tasifacte_dao.commit()
        else:
            print("Servicio proxy retorna dato nulo, posible problema con caida de servicio de rentas")
            log.info("Servicio proxy retorna dato nulo, posible problema con caida de servicio de rentas")
