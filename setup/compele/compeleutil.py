# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from setup.compele.gen_data import GenDataForFacte
from setup.compele.notificacion import NotifCompeUtil
from setup.compele.proxy import ProxyClient
from setup.models.conf import BaseDao
from setup.models.tasifacte.tasifacte_dao import TasiFacteDao

log = logging.getLogger(__name__)


class CompeleUtil(BaseDao):

    def get_data_for_contrib_save(self, trn_codigo, emp_esquema):
        pass

    def test_envio_email(self, trn_codigo, clave_acceso):
        notif = NotifCompeUtil(self.dbsession)
        notif.enviar_email(trn_codigo=trn_codigo, claveacceso=clave_acceso)

    def autorizar(self, trn_codigo):
        client_proxy = ProxyClient(self.dbsession)
        asifactedao = TasiFacteDao(self.dbsession)

        clave_tipamb = asifactedao.get_clave_acceso_ambiente(trn_codigo=trn_codigo)
        alm_ruc = ""
        tfe_ambiente = clave_tipamb['tfe_ambiente']
        clave_acceso = clave_tipamb['tfe_claveacceso']
        proxy_response = client_proxy.consulta_autorizacion(claveacceso=clave_acceso,
                                                            ambiente=tfe_ambiente,
                                                            ruc_empresa=alm_ruc)
        gen_data = GenDataForFacte(self.dbsession)
        if proxy_response is not None:
            gen_data.save_proxy_send_response(trn_codigo=trn_codigo, ambiente=tfe_ambiente,
                                              proxy_response=proxy_response)
            estado_autoriza = 0
            try:
                estado_autoriza = int(proxy_response['estado'])
            except Exception as ex:
                log.error("Error al tratar de obtener respuesta de autorizacion proxy_response['estado']", ex)

            if proxy_response['claveAcceso'] is not None and estado_autoriza == 1:
                try:
                    notif = NotifCompeUtil(self.dbsession)
                    notif.enviar_email(trn_codigo=trn_codigo, claveacceso=clave_acceso)
                except Exception as ex:
                    log.error("Error al tratar de enviar notificacion ", ex)
