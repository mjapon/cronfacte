# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging
from logging.handlers import RotatingFileHandler

from setup.compele.gen_data import GenDataForFacte
from setup.compele.gen_xml import GeneraFacturaCompEle
from setup.compele.notificacion import NotifCompeUtil
from setup.compele.proxy import ProxyClient
from setup.models.conf import BaseDao
from setup.models.tasifacte.tasifacte_dao import TasiFacteDao
from setup.models.tseccion.tseccion_dao import TSeccionDao
from setup.models.ttransaccrel.ttransaccrel_dao import TTransaccRelDao
from setup.utils import ctes, ctes_facte

rutalogs = "/var/log/cronface.log"

logging.basicConfig(handlers=[RotatingFileHandler(filename=rutalogs,
                                                  mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y%I:%M:%S %p')

log = logging.getLogger(__name__)


class CompeleUtil(BaseDao):

    def get_data_for_contrib_save(self, trn_codigo, emp_esquema):
        pass

    def test_envio_email(self, trn_codigo):
        notif = NotifCompeUtil(self.dbsession)
        asifactedao = TasiFacteDao(self.dbsession)

        clave_tipamb = asifactedao.get_clave_acceso_ambiente(trn_codigo=trn_codigo)
        clave_acceso = clave_tipamb['tfe_claveacceso']
        notif.enviar_email_documento(trn_codigo=trn_codigo, claveacceso=clave_acceso)

    def autorizar(self, trn_codigo):
        client_proxy = ProxyClient(self.dbsession)
        asifactedao = TasiFacteDao(self.dbsession)
        gen_data = GenDataForFacte(self.dbsession)
        clave_tipamb = asifactedao.get_clave_acceso_ambiente(trn_codigo=trn_codigo)
        alm_ruc = ""
        tfe_ambiente = clave_tipamb['tfe_ambiente']
        clave_acceso = clave_tipamb['tfe_claveacceso']
        if clave_acceso == '{tfe_claveacceso}' or clave_acceso == '_':
            clave_acceso = self.gen_clave_acceso(trn_codigo)

        proxy_response = client_proxy.consulta_autorizacion(claveacceso=clave_acceso,
                                                            ambiente=tfe_ambiente,
                                                            ruc_empresa=alm_ruc)

        if proxy_response is not None:
            try:
                gen_data.save_proxy_send_response(trn_codigo=trn_codigo, ambiente=tfe_ambiente,
                                                  proxy_response=proxy_response)
            except Exception as ex:
                log.info('Error al tratar de guardar respuesta autorizacion' + str(ex))
            estado_autoriza = 0
            try:
                estado_autoriza = int(proxy_response['estado'])
            except Exception as ex:
                log.info("Error al tratar de obtener respuesta de autorizacion proxy_response['estado']", ex)

            if proxy_response['claveAcceso'] is not None and estado_autoriza == 1:
                try:
                    notif = NotifCompeUtil(self.dbsession)
                    notif.enviar_email_documento(trn_codigo=trn_codigo, claveacceso=clave_acceso)
                except Exception as ex:
                    log.info("Error al tratar de enviar notificacion " + str(ex))

    def gen_clave_acceso(self, trn_codigo):
        gen_fact = GeneraFacturaCompEle(self.dbsession)
        gen_data = GenDataForFacte(self.dbsession)
        datos_fact = gen_data.get_factura_data(trn_codigo=trn_codigo)
        tra_codigo = datos_fact['tra_codigo']

        datos_factura = datos_fact['cabecera']
        sec_codigo = datos_factura['sec_codigo']
        datos_alm_matriz = gen_data.get_datos_alm_matriz(sec_codigo=sec_codigo)
        ambiente_facte = datos_alm_matriz['alm_tipoamb']

        tsecciondao = TSeccionDao(self.dbsession)

        # Check multiple secciones
        sec_id = sec_codigo
        sec_tipoamb = 0
        aplica_facte_por_seccion = False
        if sec_id is not None and int(sec_id) > 1:
            sec_tipoamb = tsecciondao.get_sec_tipoamb(sec_id=sec_codigo)
            aplica_facte_por_seccion = sec_tipoamb > 0

        if not aplica_facte_por_seccion:
            alm_tipoamb = ambiente_facte
        else:
            alm_tipoamb = sec_tipoamb

        tipo_comprobante = ctes_facte.COD_DOC_FACTURA
        if tra_codigo == ctes.TRA_COD_NOTA_CREDITO:
            tipo_comprobante = ctes_facte.COD_DOC_NOTA_CREDITO

        clave_acceso_value = gen_fact.get_clave_acceso(datos_factura=datos_factura,
                                                       tipo_ambiente=str(alm_tipoamb),
                                                       tipo_comprobante=tipo_comprobante)
        return clave_acceso_value

    def enviar_nota_credito(self, trn_notacred, sec_codigo):

        gen_fact = GeneraFacturaCompEle(self.dbsession)

        gen_data = GenDataForFacte(self.dbsession)
        datos_notacred = gen_data.get_factura_data(trn_codigo=trn_notacred)
        datos_alm_matriz = gen_data.get_datos_alm_matriz(sec_codigo=sec_codigo)

        ttransaccreldao = TTransaccRelDao(self.dbsession)
        datos_factura = ttransaccreldao.get_datos_factura_for_nota_credito(trn_notacred=trn_notacred)

        ambiente_facte = datos_alm_matriz['alm_tipoamb']

        xml_notacred_response = gen_fact.generar_nota_credito(ambiente_value=ambiente_facte,
                                                              datos_notacred=datos_notacred['cabecera'],
                                                              datos_alm_matriz=datos_alm_matriz,
                                                              totales=datos_notacred['totales'],
                                                              datos_factura_anul=datos_factura,
                                                              detalles_db=datos_notacred['detalles'])
        claveacceso = xml_notacred_response['clave']
        alm_ruc = datos_notacred['cabecera']['alm_ruc']

        client_proxy = ProxyClient(self.dbsession)

        proxy_response = None
        try:
            proxy_response = client_proxy.enviar_comprobante(claveacceso=claveacceso,
                                                             comprobante=xml_notacred_response['xml'],
                                                             ambiente=ambiente_facte, ruc_empresa=alm_ruc)
        except Exception as ex:
            log.error("Error al tratar de enviar el comprobante al sri", ex)

        enviado = False
        estado_envio = 4  # Sin transmitir
        if proxy_response is not None:
            proxy_response['numeroAutorizacion'] = claveacceso
            if proxy_response['claveAcceso'] is None:
                proxy_response['claveAcceso'] = claveacceso

            estado_envio = proxy_response['estado']
            gen_data.save_proxy_send_response(trn_codigo=trn_notacred, ambiente=ambiente_facte,
                                              proxy_response=proxy_response)
            enviado = True
        else:
            gen_data.save_proxy_send_response(trn_codigo=trn_notacred, ambiente=ambiente_facte,
                                              proxy_response={
                                                  'estado': 4,
                                                  'estadoSRI': '',
                                                  'fechaAutorizacion': '',
                                                  'mensajes': '',
                                                  'numeroAutorizacion': claveacceso,
                                                  'claveAcceso': claveacceso
                                              })
        return {'status': 200, 'exito': True, 'enviado': enviado, 'proxyresponse': proxy_response,
                'estado_envio': estado_envio}

    def enviar(self, trn_codigo):
        gen_fact = GeneraFacturaCompEle(self.dbsession)

        gen_data = GenDataForFacte(self.dbsession)
        datos_fact = gen_data.get_factura_data(trn_codigo=trn_codigo)
        tra_codigo = datos_fact['tra_codigo']
        if tra_codigo == ctes.TRA_COD_NOTA_CREDITO:
            self.enviar_nota_credito(trn_notacred=trn_codigo, sec_codigo=datos_fact['sec_codigo'])

        else:
            datos_factura = datos_fact['cabecera']
            sec_codigo = datos_factura['sec_codigo']
            datos_alm_matriz = gen_data.get_datos_alm_matriz(sec_codigo=sec_codigo)
            ambiente_facte = datos_alm_matriz['alm_tipoamb']

            tsecciondao = TSeccionDao(self.dbsession)

            # Check multiple secciones
            sec_id = sec_codigo
            sec_tipoamb = 0
            aplica_facte_por_seccion = False
            if sec_id is not None and int(sec_id) > 1:
                sec_tipoamb = tsecciondao.get_sec_tipoamb(sec_id=sec_codigo)
                aplica_facte_por_seccion = sec_tipoamb > 0

            if not aplica_facte_por_seccion:
                alm_tipoamb = ambiente_facte
            else:
                alm_tipoamb = sec_tipoamb

            xml_facte = gen_fact.generar_factura(ambiente_value=alm_tipoamb,
                                                 datos_factura=datos_factura,
                                                 datos_alm_matriz=datos_alm_matriz,
                                                 totales=datos_fact['totales'],
                                                 detalles_db=datos_fact['detalles']
                                                 )

            claveacceso = xml_facte['clave']
            alm_ruc = datos_fact['cabecera']['alm_ruc']

            client_proxy = ProxyClient(self.dbsession)

            proxy_response = None
            try:
                proxy_response = client_proxy.enviar_comprobante(claveacceso=claveacceso, comprobante=xml_facte['xml'],
                                                                 ambiente=ambiente_facte, ruc_empresa=alm_ruc)
            except Exception as ex:
                log.info("Error al tratar de enviar el comprobante al sri " + str(ex))

            enviado = False
            estado_envio = 0  # No enviado
            if proxy_response is not None:
                proxy_response['numeroAutorizacion'] = claveacceso
                if proxy_response['claveAcceso'] is None:
                    proxy_response['claveAcceso'] = claveacceso

                estado_envio = proxy_response['estado']
                try:
                    gen_data.save_proxy_send_response(trn_codigo=trn_codigo, ambiente=ambiente_facte,
                                                      proxy_response=proxy_response)
                    enviado = True
                except Exception as ex:
                    log.info("Error al tratar de guardar respuesta de envio", ex)
            else:
                gen_data.save_proxy_send_response(trn_codigo=trn_codigo, ambiente=ambiente_facte,
                                                  proxy_response={
                                                      'estado': 4,
                                                      'estadoSRI': '',
                                                      'fechaAutorizacion': '',
                                                      'mensajes': '',
                                                      'numeroAutorizacion': claveacceso,
                                                      'claveAcceso': claveacceso
                                                  })

        """
        try:
            message = {
                "emp_codigo": emp_codigo,
                "emp_esquema": emp_esquema,
                "trn_codigo": trn_codigo,
                "clave_acceso": claveacceso
            }

            str_message = self.myjsonutil.dumps(message)
            self.redispublis.publish_message(str_message)

        except Exception as ex:
            log.error("Error al tratar de enviar mensaje a la cola de comprobantes electronicos", ex)
        """

        return {'status': 200, 'exito': True, 'enviado': enviado, 'proxyresponse': proxy_response,
                'estado_envio': estado_envio}
