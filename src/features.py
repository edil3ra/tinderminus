import json
import os
import logging
import time
import random
import yaml
from typing import List, Optional
from pynder.models import User
from pynderProxySession import Session
import json
import requests
import urllib
from tqdm import tqdm
from enum import Enum


class Choice(Enum):
    DISLIKE = 0
    LIKE = 1
    SUPERLIKE = 2


DATA_DIR = os.path.join('..', 'data')
IMAGE_DIR = os.path.abspath(os.path.join(DATA_DIR, 'images'))
USERS_FILE = os.path.abspath('../data/users.json')

if not os.path.isfile(USERS_FILE):
    open(USERS_FILE, 'w').write(json.dumps({}))

if not os.path.isdir(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)


LOGGER_PATH = os.path.abspath('../conf/logging.yaml')
logger_config = yaml.load(open((LOGGER_PATH)).read())
logging.config.dictConfig(logger_config)


def get_users(session: Session,
              count: int=10,
              time_to_wait: float=0,
              randomize_wait: float=0,
              limit: int=10) -> List[User]:
    '''
    Return users from with the session
    Parameters
    ---------
        session: Session
             The pynderProxySession or Session fro pynder instance
        count: int
            Numbers of users to ge
        time_to_wait: float
            Time_to_wait: time to wait between getting one user
        randomize_wait: float (0, 1)
            Wait for a random fraction of randomize_wait
        limit: int
            Limit to call the pynder recomendation
    Returns
    -------
        List[User]
             return a list of users
    '''
    users_generator = session.nearby_users(limit)
    users = []
    for i in range(count):
        next_user = next(users_generator)
        users.append(next_user)

        if time_to_wait < -1:
            raise ValueError('time_to_wait must be positive')
        if not (0 <= randomize_wait <= 1):
            raise ValueError('randomize_wait must be between 0 and 1')

        if time_to_wait != 0:
            wait_for = time_to_wait + (
                randomize_wait * random.random() * random.choice([-1, 1]))
            logging.info('wait for: {}'.format(wait_for))
            time.sleep(wait_for)
    return users


def like_users(users: List[User]) -> None:
    '''
    like every users
    Parameters
    ---------
         users: List[user]
    Returns
    ------
         None
    '''
    for user in users:
        user.like()
        


def dislike_users(users: List[User]) -> None:
    '''
    diskile every users
    Parameters
    ---------
         users: List[user]
    Returns
    ------
        None
    '''
    for user in users:
        user.diskile()
        

def superlike_user(user: User) -> None:
    '''
    super like an user (proy to user.superlike)
    Parameters
    ---------
         user: User
    Returns
    ------
         None
    '''
    user.superlike()

        
def swipe_random_users(users: List[User], percent: float=0.8) -> List[User]:
    '''
    random every users
    Parameters
    ---------
         users: List[User]
         percent: float
    Returns
    ------
        (List[User], List[User]) list of like and diskile user
    '''
    matches = []
    likes = [(user, True) for user in users[0:int(len(users) * percent)]]
    dislikes = [(user, False) for user in users[int(len(users) * percent):]]
    users_randoms = likes + dislikes
    random.shuffle(users_randoms)

    for (user, like) in users_randoms:
        if like:
            user.like()
        else:
            user.diskile()
    return (likes, dislikes)

    
def save_users(users: List[User],
               choice: int=Choice.LIKE,
               save_image=True) -> None:
    '''
    save users into json files (constast file for know)
    check if the content has changed to add users
    Parameters
    ----------
          users: List[User]
          choice: int | Choice.DISLIKE, Choice.LIKE
          save_image: bool | true if you want to save the images
    Returns
    -------
          None
    '''
    users_to_update = {
        user.id: {'like': cohice, 'data': user._data}
        for user in users
    }
    logging.info('save to file '.format(USERS_FILE))
    users_from_json = json.load(open(USERS_FILE, 'r'))
    users_from_json.update(users_to_update)
    json.dump(users_from_json, open(USERS_FILE, 'w'))

    if save_image:
        pbar = tqdm(users)
        for user in pbar:
            pbar.set_description('Processing: '.format(user.id))
            download_image_from_user(user)
            

def load_users(ids: List[int], session) -> List[User]:
    '''
    return a list of users registered given the users ids
    Parameters
    ----------
          ids: List[int]
          session: Session
    Returns
    -------
          List[User]
    '''
    pass


def download_image_from_user(user: User) -> None:
    '''
    download the image for one user
    Parameters
    ----------
          user: User
    Returns
    -------
          None
    '''
    
    photos = user.photos
    for photo in photos:
        url_info = urllib.parse.urlparse(photo)
        path = url_info.path
        logging.info('downloading image for: {}'.format(user.id))
        response = requests.get(photo)
        image_name = path.split('/')[-1]
        image_filename = '{}-{}'.format(user.id, image_name)
        image_path = os.path.join(IMAGE_DIR, image_filename)
        with open(image_path, 'wb') as f:
            f.write(response.content)
