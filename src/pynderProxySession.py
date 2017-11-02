import time
import random
import json
import os
import logging
import logging.config
import yaml
from pynder import Session as PynderSession
from pynder import api

DATA_DIR = os.path.abspath('../data')
LOGGER_PATH = os.path.abspath('../conf/logging.yaml')

logger_config = yaml.load(open((LOGGER_PATH)).read())
logging.config.dictConfig(logger_config)
logger = logging.getLogger('root')

class Session(PynderSession):
    def __init__(self, facebook_token=None, XAuthToken=None, proxies=None, facebook_id=None, cert=None):
        if facebook_token is None and XAuthToken is None:
            raise InitializationError("Either XAuth or facebook token must be set")

        self._api = api.TinderAPI(XAuthToken, proxies)
        if proxies is not None:
            self._api._session.cert = cert
            self._api._session.verify = False
        # perform authentication
        if XAuthToken is None:
            self._api.auth(facebook_id, facebook_token)

    def get_users(self, n=10, time_to_wait=None, randomize_wait=None, limit=10):
        ''' return a list contains n users
            n: the number of users to return
            time_to_wait: float in second
            randomize_wait: Bool
            list of users
        '''
        users_gen = self.nearby_users(limit)
        users = []
        for i in range(n):
            next_user = next(users_gen)
            users.append(next_user)
            
            if time_to_wait is not None:
                if randomize_wait is not None:
                    if random.choice([0, 1]) == 0:
                        time.sleep(time_to_wait + random.random() * time_to_wait)
                    else:
                        time.sleep(time_to_wait - random.random() * time_to_wait)
                time.sleep(time_to_wait)
                logger.info('sleeep for: {}'.format(time_to_wait))
        return users

    
    def save_user(self, user):
        filename = '{}.json'.format(user.id)
        path = os.path.join(DATA_DIR, filename)
        open(path, 'w').write(json.dumps(user._data))


    def save_users(self, users):
        for user in users:
            self.save_user(user)

   
    def swipe_all(self, users):
        for user in users:
            user.like()


            
