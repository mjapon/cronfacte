# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

import redis

from setup.compele.compeleutil import CompeleUtil
from setup.models.conf import BaseDao
from setup.utils.jsonutil import SimpleJsonUtil

log = logging.getLogger(__name__)

simplejsonutil = SimpleJsonUtil()

"""
PASS_REDIS_PROD = "Hart$$471"
myredis = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True, password=PASS_REDIS_PROD)
"""

myredis = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)


class RedisSubscriber(BaseDao):

    def __init__(self, dbsession):
        super(RedisSubscriber, self).__init__(dbsession, '')
        self.channel = 'facturas'
        # self.connect()
        self.listen()
        self.delay = 4

    # def connect(self):
    # self.red = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

    def save_contrib(self, trn_codigo, emp_esquema):
        try:
            compeleutil = CompeleUtil(self.dbsession)
            compeleutil.set_esquema(emp_esquema)

        except Exception as ex:
            log.error("Error al tratar de realizar registro de contribuyente", ex)

    def autorizar(self, trn_codigo, emp_esquema):
        try:
            compeleutil = CompeleUtil(self.dbsession)
            compeleutil.set_esquema(emp_esquema)
            compeleutil.autorizar(trn_codigo)
            log.info("Termina procesamiento de mensaje: trn_codigo={0}".format(trn_codigo))
        except Exception as ex:
            log.error("Error al tratar de realizar consulta de autorizacion", ex)

    def process_message(self, message_dict):
        log.info("Entra a procesar mensaje: trn_codigo={0}, emp_esquema:{1}".format(
            message_dict['trn_codigo'],
            message_dict['emp_esquema']
        ))
        accion = message_dict['accion']
        if accion == 'autoriza':
            self.autorizar(trn_codigo=message_dict['trn_codigo'],
                           emp_esquema=message_dict['emp_esquema'])
        elif accion == 'savecontrib':
            pass
            """
            self.save_contrib(trn_codigo=message_dict['trn_codigo'],
                              emp_esquema=message_dict['emp_esquema'])
            """

    def listen(self):
        sub = myredis.pubsub()
        sub.subscribe(self.channel)
        for message in sub.listen():
            try:
                if message is not None and isinstance(message, dict):
                    print("llega mensaje-->")
                    print(message)
                    strmessage = message.get('data')
                    objmesage = simplejsonutil.obj(str(strmessage))
                    if isinstance(objmesage, dict):
                        self.process_message(objmesage)
            except Exception as ex:
                log.error("Error al leer mensaje: {0}".format(ex))

    def start_listen(self):
        while True:
            self.listen()
