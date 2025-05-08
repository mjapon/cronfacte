# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging
from logging.handlers import RotatingFileHandler

from setup.models.conf import BaseDao
from setup.models.tasiento.tasiento_dao import TAsientoDao
from setup.models.tasifacte.tasifacte_dao import TasiFacteDao
from setup.models.tcomprobante.tcomprobante_dao import TComprobanteDao
from setup.models.tcontribuyente.tcontribuyente_dao import TContribuyenteDao
from setup.utils import ctes_facte

rutalogs = "/var/log/cronface.log"
# rutalogs = "C:\\dev\\mavil\\logs\\cronface.log"

logging.basicConfig(handlers=[RotatingFileHandler(filename=rutalogs,
                                                  mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y%I:%M:%S %p')

log = logging.getLogger(__name__)


class GenDataForFacte(BaseDao):

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
                per.per_direccion,
                per.per_nombres,
                per.per_apellidos,
                per.per_telf,
                per.per_movil,
                per.per_email,
                asi.trn_compro,
                asi.sec_codigo,
                asi.tra_codigo 
                from tasiento asi
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
                      'per_direccion',
                      'per_nombres',
                      'per_apellidos',
                      'per_telf',
                      'per_movil',
                      'per_email',
                      'trn_compro',
                      'sec_codigo',
                      'tra_codigo'
                      )

        datos_factura = self.first(sql, tupla_desc)

        tasidao = TAsientoDao(self.dbsession)
        detalles = tasidao.get_detdoc_foredit(trn_codigo=trn_codigo, dt_tipoitem=1)
        pagos = tasidao.get_detalles_doc(trn_codigo=trn_codigo, dt_tipoitem=2, joinarts=False)
        totales = tasidao.calcular_totales(detalles)

        totales_facte = {
            'total_sin_impuesto': totales['subtotal'] - totales['descuentos'],
            'total_descuentos': totales['descuentos'],
            'base_imp_iva_12': totales['subtotal12'],
            'impuesto_iva_12': totales['iva'],
            'base_imp_iva_15': totales['subtotal15'],
            'impuesto_iva_15': totales['iva15'],
            'base_imp_iva_5': totales['subtotal5'],
            'impuesto_iva_5': totales['iva5'],
            'total': totales['total'],
            'pago_efectivo': totales['total'],
            'pago_credito': 0,  # TODO:
        }

        return {'cabecera': datos_factura,
                'detalles': detalles,
                'pagos': pagos,
                'totales': totales_facte}

    def get_datos_alm_matriz(self, sec_codigo):
        sqlbase = """
        select  alm.alm_codigo,
                alm_numest,
                alm_razsoc,
                alm_descri,
                alm_direcc,
                alm_repleg,
                alm_email,
                alm_websit,
                alm_fono1,
                alm_fono2,
                alm_movil,
                alm_ruc,
                alm_ciudad,
                alm_sector,
                alm_fecreg,
                cnt_codigo,
                alm_matriz,
                alm_tipoamb,
                alm_nomcomercial,
                alm_contab from talmacen alm
        """

        where = " where alm_matriz = 1 "
        if int(sec_codigo) > 1:
            where = """
            join tseccion sec on alm.alm_codigo = sec.alm_codigo 
            where sec.sec_id = {0}
            """.format(sec_codigo)

        sql = "{0} {1}".format(sqlbase, where)

        tupla_desc = (
            'alm_codigo',
            'alm_numest',
            'alm_razsoc',
            'alm_descri',
            'alm_direcc',
            'alm_repleg',
            'alm_email',
            'alm_websit',
            'alm_fono1',
            'alm_fono2',
            'alm_movil',
            'alm_ruc',
            'alm_ciudad',
            'alm_sector',
            'alm_fecreg',
            'cnt_codigo',
            'alm_matriz',
            'alm_tipoamb',
            'alm_nomcomercial',
            'alm_contab'
        )

        return self.first(sql, tupla_desc)

    def get_proxy_key_value(self, key, proxy_response):
        return proxy_response[key] if key in proxy_response else ''

    def save_proxy_send_response(self, trn_codigo, ambiente, proxy_response):
        try:
            tasifacte_dao = TasiFacteDao(self.dbsession)
            data = {
                'tfe_estado': self.get_proxy_key_value('estado', proxy_response),
                'tfe_estadosri': self.get_proxy_key_value('estadoSRI', proxy_response),
                'tfe_fecautoriza': self.get_proxy_key_value('fechaAutorizacion', proxy_response),
                'tfe_mensajes': str(self.get_proxy_key_value('mensajes', proxy_response)),
                'tfe_numautoriza': self.get_proxy_key_value('numeroAutorizacion', proxy_response),
                'tfe_ambiente': ambiente,
                'tfe_claveacceso': self.get_proxy_key_value('claveAcceso', proxy_response)
            }

            mensajes = proxy_response['mensajes'] if 'mensajes' in proxy_response else []
            if mensajes is not None:
                for mensaje in mensajes:
                    msg = str(mensaje)
                    if "CLAVE ACCESO REGISTRADA" in msg and "identificador = \"43\"" in msg:
                        data['tfe_estado'] = 1
                        proxy_response['estado'] = 1
                        data['tfe_estadosri'] = 'AUTORIZADO'
                        data['tfe_mensajes'] = 'MAVIL:Actualizado a autorizado por error de CLAVE-ACCESO-REGISTRADA'

            tasifacte_dao.create_or_update(trn_codigo=trn_codigo, data=data)
            log.info('tasifacte actualizado')
        except Exception as ex:
            log.info('Error en save_proxy_send_response ' + str(ex))

    def save_contrib_and_compro(self, datosfact, claveacceso, trn_cod, emp_codigo, total_fact, estado_envio,
                                ambiente):
        self.set_esquema(ctes_facte.ESQUEMA_FACTE_COMPROBANTES)
        tcontribdao = TContribuyenteDao(self.dbsession)
        tcomprobdao = TComprobanteDao(self.dbsession)

        form_contrib = {
            'cnt_ciruc': datosfact['per_ciruc'],
            'cnt_nombres': datosfact['per_nombres'],
            'cnt_apellidos': datosfact['per_apellidos'],
            'cnt_direccion': datosfact['per_direccion'],
            'cnt_telf': datosfact['per_telf'],
            'cnt_email': datosfact['per_email'],
            'cnt_movil': datosfact['per_movil']
        }
        cnt_id = tcontribdao.create_or_update(form=form_contrib)

        form_comprob = {
            'cmp_claveaccesso': claveacceso,
            'cmp_tipo': ctes_facte.COD_DOC_FACTURA,
            'cmp_numero': datosfact['trn_compro'],
            'cmp_trncod': trn_cod,
            'cnt_id': cnt_id,
            'emp_codigo': emp_codigo,
            'cmp_fecha': datosfact['trn_fecreg'],
            'cmp_total': total_fact,
            'cmp_estado': estado_envio,
            'cmp_ambiente': ambiente
        }

        tcomprobdao.crear(form=form_comprob)
