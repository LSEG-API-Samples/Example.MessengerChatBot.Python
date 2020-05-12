# |-----------------------------------------------------------------------------
# |            This source code is provided under the Apache 2.0 license      --
# |  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
# |                See the project's LICENSE.md for details.                  --
# |           Copyright Refinitiv 2020. All rights reserved.                  --
# |-----------------------------------------------------------------------------

# |-----------------------------------------------------------------------------
# |         Refinitiv Data Platform demo app/module to change RDP Password    --
# |-----------------------------------------------------------------------------

# Import the required libraries for HTTP/JSON operations
import requests
import json
import time
import logging

_username = ''
_old_password = ''
_new_password = ''
_client_id = ''
client_secret = ''

scope = 'trapi.messenger'

rdp_authen_version = '/v1'
base_URL = 'https://api.refinitiv.com'
category_URL = '/auth/oauth2'

authen_URL = '{}{}{}/token'.format(base_URL,category_URL, rdp_authen_version)

# Create new RDP Change Password request message and send it to RDP service
def change_password(username, old_password, client_id, new_password):

    # Create request message
    change_password_req_msg = {
        'grant_type': 'password',
        'username': username,
        'password': old_password,
        'newPassword': new_password,
        'scope': scope,
        'takeExclusiveSignOnControl': 'true'
    }


    logging.debug('Sent: %s' % (json.dumps(change_password_req_msg, sort_keys=True, indent=2, separators=(',', ':'))))

    try:
        response = requests.post(authen_URL,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'},
                data=change_password_req_msg,
                auth=(
                    client_id,
                    client_secret
                ))
    except requests.exceptions.RequestException as e:
        logging.error('RDP Change Password exception failure: %s' % (e))

    if response.status_code == 200:  # HTTP Status 'OK'
        print('Change Password success')
        # Print RDP Change Password response message for debugging purpose
        logging.debug('Receive: %s' % (json.dumps(response.json(), sort_keys=True, indent=2, separators=(',', ':'))))

    else:
        logging.error('RDP Change Password result failure: %s %s' % (response.status_code, response.reason))
        logging.error('Text: %s' % (response.text))

    return response.status_code, response.json()

# =============================== Main Process, For verifying your RDP Account purpose ============================
if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s: %(levelname)s:%(name)s :%(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

    print('Chaning RDP Auth Service Password')

    # Authentication Variables
    _username = '---YOUR BOT USERNAME---'
    _old_password = '---YOUR BOT OLD PASSWORD---'
    _client_id = '---YOUR MESSENGER ACCOUNT APPKEY---'
    _new_password = '---YOUR BOT NEW PASSWORD---'

    """
    Input above RDP credentials information and run this module with the following command in a console
    $>python rdp_change_password_demo.py
    """

    change_password(username = _username, old_password = _old_password, client_id = _client_id, new_password = _new_password)