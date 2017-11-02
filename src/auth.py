import re
import logging
import logging.config

import robobrowser
import requests


def get_facebook_token_and_id(email, password):
    MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; U; en-gb; KFTHWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.16 Safari/535.19"
    FB_API_KEY_URL = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"
    
    FB_API_KEY_ID = 'https://graph.facebook.com/v2.6/me?fields=id&access_token={}'
    rb = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="html5lib")
    
    # Read Facebook cookies
    rb.open(FB_API_KEY_URL)
    login_form = rb.get_form()
    login_form["pass"] = password
    login_form["email"] = email
    rb.submit_form(login_form)

    # Get token
    auth_form = rb.get_form()
    rb.submit_form(auth_form, submit=auth_form.submit_fields["__CONFIRM__"])
    facebook_token = re.search(r"access_token=([\w\d]+)", rb.response.content.decode()).groups()[0]
    facebook_id = requests.get(FB_API_KEY_ID.format(facebook_token)).json()['id']
    
    return facebook_token, facebook_id

