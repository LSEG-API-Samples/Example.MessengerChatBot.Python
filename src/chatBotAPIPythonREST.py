import requests
import json
import sys
from rdpToken import rdpToken

# Authentication Variables
bot_username = ''
bot_password = ''
bot_app_key = ''

# Authentication objects
auth_token = None
rdp_token = None


def connect():
    global rdp_token
    auth_token = rdp_token.get_token()
    return auth_token


def list_chatrooms(room_is_managed=False):
    global auth_token

    if room_is_managed:
        url = 'https://api.refinitiv.com/messenger/beta1/managed_chatrooms'
    else:
        url = 'https://api.refinitiv.com/messenger/beta1/chatrooms'

    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer {}'.format(auth_token['access_token'])}
    response = None
    try:
        # Send request message to RDP with Python requests module
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print('RDP authentication exception failure:', e)

    if response.status_code == 200:
        print('Messenger BOT API get chatroom  success')
    else:
        print('Messenger BOT API get chatroom result failure:',
              response.status_code, response.reason)
        print('Text:', response.text)

    return response.status_code, response.json()

# =============================================================================


if __name__ == '__main__':
    print('Getting RDP Authentication Token')

    rdp_token = rdpToken(bot_username, bot_password, bot_app_key)
    auth_token = connect()

    if not auth_token:
        sys.exit(1)
    print('Successfully Authenticated ')

    print('Get Rooms ')
    status, chatroomId = list_chatrooms()
    print(json.dumps(chatroomId, sort_keys=True,
                     indent=2, separators=(',', ':')))
