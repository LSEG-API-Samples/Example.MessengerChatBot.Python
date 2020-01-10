# |-----------------------------------------------------------------------------
# |            This source code is provided under the Apache 2.0 license      --
# |  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
# |                See the project's LICENSE.md for details.                  --
# |           Copyright Refinitiv 2020. All rights reserved.                  --
# |-----------------------------------------------------------------------------

# |-----------------------------------------------------------------------------
# |            Refinitiv Data Platform demo app to get OAuth tokens           --
# |-----------------------------------------------------------------------------

# Import the required libraries for HTTP/JSON operations
import requests
import json
import time
import logging

# Authentication objects
auth_obj = None

# Authentication Variables
_username = 'XXXXX'
_password = 'XXXXX'
_app_key = 'XXXXX'


class RDPTokenManagement:
    # Authentication Variables
    username = ''
    password = ''
    app_key = ''
    client_secret = ''
    before_timeout = 0

    # Create a custom logger
    # logger = logging.getLogger(__name__)
    # create console handler
    # console_logger = logging.StreamHandler()

    # RDP Authentication Service Detail
    rdp_authen_version = '/v1'
    base_URL = 'https://api.refinitiv.com'
    category_URL = '/auth/oauth2'
    #endpoint_URL = '/token'
    token_file = './token.txt'
    scope = 'trapi.messenger'

    # Create RDP Authentication service URL
    #authen_URL = base_URL + category_URL + rdp_authen_version + endpoint_URL
    authen_URL = '{}{}{}/token'.format(base_URL,
                                       category_URL, rdp_authen_version)

    def __init__(self, username, password, app_key,  before_timeout=10):
        self.username = username
        self.password = password
        self.app_key = app_key
        self.before_timeout = before_timeout

    # Create new RDP Authentication request message and send it to RDP service
    def request_new_token(self, refresh_token):

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
            response = requests.post(self.authen_URL,
                                     headers={
                                         'Accept': 'application/json',
                                         'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=authen_request_msg,
                                     auth=(
                                         self.app_key,
                                         self.client_secret
                                     ))
        except requests.exceptions.RequestException as e:
            print('RDP authentication exception failure:', e)

        if response.status_code == 200:  # HTTP Status 'OK'
            print('Authenticaion success')
            # Print RDP authentication response message for debugging purpose
            logging.debug('Receive: %s' % (json.dumps(
                response.json(), sort_keys=True, indent=2, separators=(',', ':'))))
        else:  # Handle HTTP error
            print('RDP authentication result failure:',
                  response.status_code, response.reason)
            print('Text:', response.text)
            # both access and refresh tokens are expired
            if response.status_code == 400 and response.json()['error'] == 'invalid_grant':
                print('Both Access Token and Refresh Token are expired')
                raise Exception('Both Access Token and Refresh Token are expired {0} - {1}'
                                .format(response.status_code, response.text))
        return response.status_code, response.json()

    # Create new RDP Change Password request message and send it to RDP service
    def change_password(_username, old_password, client_id, new_password):

        # Create request message
        change_password_req_msg = {
            'grant_type': 'password',
            'username': _username,
            'password': old_password,
            'newPassword': new_password,
            'scope': scope,
            'takeExclusiveSignOnControl': 'true'
        }

        # Print for debugging purpose
        logging.debug('Sent: %s' % (json.dumps(
            change_password_req_msg, sort_keys=True, indent=2, separators=(',', ':'))))

        try:
            response = requests.post(self.authen_URL,
                                     headers={
                                         'Accept': 'application/json',
                                         'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=authen_request_msg,
                                     auth=(
                                         app_key,
                                         client_secret
                                     ))
        except requests.exceptions.RequestException as e:
            print('RDP Change Password exception failure:', e)

        if response.status_code == 200:  # HTTP Status 'OK'
            print('Change Password success')
            # Print RDP Change Password response message for debugging purpose
            logging.debug('Receive: %s' % (json.dumps(
                response.json(), sort_keys=True, indent=2, separators=(',', ':'))))
            self.save_authen_to_file(response.json())
        else:
            print('RDP Change Password result failure:',
                  response.status_code, response.reason)
            print('Text:', response.text)

        return response.status_code, response.json()

    # Save RDP Authentication information (Access Token, Refresh Token and Expire time) into the file
    def save_authen_to_file(self, _authen_obj):

        with open(self.token_file, 'w') as saved_token:  # Open './token.txt' file
            print('Saving Authentication information to file')
            # _authen_obj['expires_tm'] = time.time() + int(_authen_obj['expires_in']) - 10
            _authen_obj['expires_tm'] = time.time(
            ) + int(_authen_obj['expires_in']) - self.before_timeout

            json.dump(_authen_obj, saved_token, indent=4)

    # Get RDP Authentication Token from './token.txt' file first.
    # If token expire or not exist, request a new token
    def get_token(self):
        is_request_error = False
        try:
            print('Checking RDP token information in %s' % (self.token_file))
            with open(self.token_file, 'r+') as saved_token:  # Open './token.txt' file
                auth_obj = json.load(saved_token)
                if auth_obj['expires_tm'] > time.time():  # Access Token is still active
                    print('Token is still active')
                    return auth_obj

            # Access Token expire
            print('Token expired, request a new Token with a refresh token')
            status, auth_obj = self.request_new_token(
                auth_obj['refresh_token'])
        except IOError as e:
            print(e)
            print('None Token found, requesting a new one')
            is_request_error = True
        except json.JSONDecodeError as json_error:
            print(json_error)
            print('None Token found, requesting a new one')
            is_request_error = True
        except:
            print('Getting a new token...')
            is_request_error = True

        if is_request_error:  # if first request returns error, re-request RDP Access Token
            status, auth_obj = self.request_new_token(None)

        if status == 200:  # HTTP Status 'OK'
            self.save_authen_to_file(auth_obj)
            return auth_obj
        else:
            return None


# =============================================================================
if __name__ == '__main__':

    logging.basicConfig(
        format='%(levelname)s:%(name)s :%(message)s', level=logging.DEBUG)

    print('Getting RDP Authentication Token')

    rdp_token = RDPTokenManagement(
        _username, _password, _app_key, logging.WARN)
    auth_obj = rdp_token.get_token()
    if auth_obj:
        print('access token = %s' % auth_obj['access_token'])
        print('refresh token = %s' % auth_obj['refresh_token'])
        print('expires_in = %s' % auth_obj['expires_in'])
