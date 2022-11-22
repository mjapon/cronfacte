# This is a sample Python script.

import logging
from logging.handlers import RotatingFileHandler

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from setup.db import get_dbsession
# Press the green button in the gutter to run the script.
from setup.redispub.redisutil import RedisSubscriber

rutalogs = "/Users/manueljapon/Documents/dev/logs/cronface.log"
#rutalogs = "/var/log/cronface.log"

logging.basicConfig(handlers=[RotatingFileHandler(filename=rutalogs,
                                                  mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y%I:%M:%S %p')

if __name__ == '__main__':
    log = logging.getLogger('my_logger')

    log.info("cronfacte starting----->")
    print("cronfacte starting----->")
    dbsession = get_dbsession()
    """
    schema = 'fusay'
    fatedao = TasiFacteDao(dbsession, schema)
    clave = "1410202201110516177000110010010000002520000000015"
    fatedao.set_default_shema()
    res = fatedao.find_by_claveacceso(clave)

    print(res)

    data = {
        'tfe_claveacceso': '1234123412',
        'tfe_estado': 1,
        'tfe_fecautoriza': '123123',
        'tfe_mensajes': '',
        'tfe_numautoriza': '1234123143',
        'tfe_ambiente': 1,
        'tfe_estadosri': 'AUTORIZADO'
    }

    fatedao.create_or_update(trn_codigo=3, data=data)
    fatedao.commit()    
    """

    redisutil = RedisSubscriber(dbsession)
    redisutil.start_listen()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
