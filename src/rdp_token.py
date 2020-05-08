# |-----------------------------------------------------------------------------
# |            This source code is provided under the Apache 2.0 license      --
# |  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
# |                See the project's LICENSE.md for details.                  --
# |           Copyright Refinitiv 2020. All rights reserved.                  --
# |-----------------------------------------------------------------------------

# |-----------------------------------------------------------------------------
# |         Refinitiv Data Platform demo app/module to get OAuth tokens       --
# |-----------------------------------------------------------------------------

# Import the required libraries for HTTP/JSON operations
import requests
import json
import time
import logging

# Authentication objects
auth_obj = None


class RDPTokenManagement:
    # Authentication Variables
    username = ''
    password = ''
    app_key = ''
    client_secret = ''
    before_timeout = 0

    #new parameters

    access_token = ''
    refresh_token = ''

    # RDP Authentication Service Detail
    rdp_authen_version = '/v1'
    base_URL = 'https://api.refinitiv.com'
    category_URL = '/auth/oauth2'
    # endpoint_URL = '/token'
    token_file = './rest-token.txt'
    scope = 'trapi.messenger'

    # Create RDP Authentication service URL
    # authen_URL = base_URL + category_URL + rdp_authen_version + endpoint_URL
    authen_URL = '{}{}{}/token'.format(base_URL,
                                       category_URL, rdp_authen_version)

    def __init__(self, username, password, app_key,  before_timeout=10):
        self.username = username
        self.password = password
        self.app_key = app_key
        self.before_timeout = before_timeout

    # Create new RDP Authentication request message and send it to RDP service
    def request_new_token(self, refresh_token, url=None):

        if url is None:
            url = self.authen_URL

        # Create a request message
        if not refresh_token:
            authen_request_msg = {
                'username': self.username,
                'password': self.password,
                'client_id':  self.app_key,
                'grant_type': 'password',
                'scope': self.scope,
                'takeExclusiveSignOnControl': 'true'
            }
        else:
            authen_request_msg = {
                'refresh_token': refresh_token,
                'username': self.username,
                'grant_type': 'refresh_token',
            }
        response = None

        # Print for debugging purpose
        logging.debug('Sent: %s' % (json.dumps(
            authen_request_msg, sort_keys=True, indent=2, separators=(',', ':'))))
        try:
            # Send request message to RDP with Python requests module
            response = requests.post(url,
                                     headers={
                                         'Accept': 'application/json',
                                         'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=authen_request_msg,
                                     auth=(
                                         self.app_key,
                                         self.client_secret
                                     ))
        except requests.exceptions.RequestException as e:
            logging.error('RDP authentication exception failure: %s' % (e))

        if response.status_code == 200:  # HTTP Status 'OK'
            print('Authenticaion success')
            # Print RDP authentication response message for debugging purpose
            logging.debug('Receive: %s' % (json.dumps(response.json(), sort_keys=True, indent=2, separators=(',', ':'))))
        else:  # Handle HTTP error
            logging.error('RDP authentication result failure: %s %s' % (response.status_code, response.reason))
            logging.error('Text: %s' % (response.text))
            # both access and refresh tokens are expired
            #if response.status_code == 400 and (response.json()['error'] == 'invalid_grant' or response.json()['error_description'] == 'Refresh token does not exist.'):
            #    print('Both Access Token and Refresh Token are expired')
            #    raise Exception('Both Access Token and Refresh Token are expired {0} - {1}'.format(response.status_code, response.text))
            if response.status_code == 400 or response.status_code == 401:
                if refresh_token:
                    print('Retry with username and password')
                    return self.request_new_token(None)
                return None, None
            elif response.status_code == 403 or response.status_code == 451:
                print('Stop retrying with the request')
                return None, None
            elif response.status_code == 301 or response.status_code == 302 or response.status_code == 307 or response.status_code == 308:
                # Perform URL redirect
                new_host = response.headers['Location']
                if new_host is not None:
                    print('Perform URL redirect to ', new_host)
                    return self.request_new_token(refresh_token, new_host)
                return None, None, None

        return response.status_code, response.json()


    # Save RDP Authentication information (Access Token, Refresh Token and Expire time) into the file
    def save_authen_to_file(self, _authen_obj):

        with open(self.token_file, 'w') as saved_token:  # Open './token.txt' file
            print('Saving Authentication information to file')
            # _authen_obj['expires_tm'] = time.time() + int(_authen_obj['expires_in']) - 10
            _authen_obj['expires_tm'] = time.time(
            ) + int(_authen_obj['expires_in']) - self.before_timeout

            json.dump(_authen_obj, saved_token, indent=4)

    """
    Get RDP Authentication Token.
    Use save_token_to_file variable to verify if read and write RDP token to './rest-token.txt' file or not.
    
    - REST application: save_token_to_file = True. Get previous token from a file first. If token expire or not exist, request a new token. Once authentication is granted, saved Token information to a file for later use.
    - WebSocket application: save_token_to_file = False. Always request a new token to RDP without read/save a token file due to WebSocket application behavior.
    
    """

    def get_token(self, save_token_to_file=True, current_refresh_token = None):
        is_request_error = False
        try:
            if save_token_to_file: # chatbot_demo_rest.js
                print('Checking RDP token information in %s' %
                      (self.token_file))
                with open(self.token_file, 'r+') as saved_token:  # Open './token.txt' file
                    auth_obj = json.load(saved_token)
                    if auth_obj['expires_tm'] > time.time():  # Access Token is still active
                        print('Token is still active')
                        return auth_obj
                    else:
                        # Access Token expire
                        print('Token expired, request a new Token with a refresh token')
                        
                # chatbot_demo_rest.js
                status, auth_obj = self.request_new_token(auth_obj['refresh_token'])
            else: # chatbot_demo_ws.js
                status, auth_obj = self.request_new_token(current_refresh_token) 
           
        except IOError as e:
            logging.error('IOError Exception: %s' % e)
            print('None Token found, requesting a new one')
            is_request_error = True
        except json.JSONDecodeError as json_error:
            logging.error('json.JSONDecodeError Exception: %s' % json_error)
            print('None Token found, requesting a new one')
            is_request_error = True
        except:
            print('Getting a new token...')
            is_request_error = True

        if is_request_error:  # if first request returns error, re-request RDP Access Token
            status, auth_obj = self.request_new_token(None)

        if status == 200:  # HTTP Status 'OK'
            if save_token_to_file:
                self.save_authen_to_file(auth_obj)

            #new code
            self.access_token = auth_obj['access_token']
            self.refresh_token = auth_obj['refresh_token']
            return auth_obj
        else:
            return None


# =============================== Main Process, For verifying your RDP Account purpose ============================
if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s: %(levelname)s:%(name)s :%(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

    print('Getting RDP Authentication Token')

    # Authentication Variables
    _username = '---YOUR BOT USERNAME---'
    _password = '---YOUR BOT PASSWORD---'
    _app_key = '---YOUR MESSENGER ACCOUNT APPKEY---'


    """
    Input above RDP credentials information and run this module with the following command in a console
    $>python rdp_token.py
    """

    rdp_token = RDPTokenManagement(
        _username, _password, _app_key, logging.DEBUG)
    auth_obj = rdp_token.get_token()
    # auth_obj = rdp_token.get_token(save_token_to_file=False)
    if auth_obj:
        print('access token = %s' % auth_obj['access_token'])
        print('refresh token = %s' % auth_obj['refresh_token'])
        print('expires_in = %s' % auth_obj['expires_in'])
