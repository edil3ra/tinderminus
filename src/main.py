import yaml
import os
import logging
import logging.config
from pynderProxySession import Session
from auth import get_facebook_token_and_id
import click

CONFIG_PATH = os.path.abspath('../conf/conf.yaml')
LOGGER_PATH = os.path.abspath('../conf/logging.yaml')

logger_config = yaml.load(open((LOGGER_PATH)).read())
logging.config.dictConfig(logger_config)
logger = logging.getLogger('root')
config = yaml.load(open(CONFIG_PATH).read())



@click.command()
@click.option('--email', envvar='FACEBOOK_EMAIL')
@click.option('--password', envvar='FACEBOOK_PASSWORD')
@click.option('--token', envvar='FACEBOOK_TOKEN')
@click.option('--id', envvar='FACEBOOK_ID')
def app(email, password, token, id):
    session = create_session(email, password, token, id)
    
def create_session(email_arg=None, password_arg=None, token_arg=None, id_arg=None):
    email = config['facebook_email'] or email_arg
    password = config['facebook_password'] or password_arg
    id = config['facebook_id'] or id_arg
    token = config['facebook_token'] or token_arg

    if email and password:
        token, id = get_facebook_token_and_id(
            email=email,
            password=password
        )
    
    return Session(
        facebook_id=id,
        facebook_token=token,
        # proxies=config['proxies'],
        cert=os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
    )

def main():
    app()


if __name__ == '__main__':
    main()
