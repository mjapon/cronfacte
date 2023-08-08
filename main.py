import logging
from logging.handlers import RotatingFileHandler

from setup.db import get_dbsession
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

    redisutil = RedisSubscriber(dbsession)

    redisutil.start_listen()
