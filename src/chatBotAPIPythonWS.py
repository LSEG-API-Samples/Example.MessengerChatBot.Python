# |-----------------------------------------------------------------------------
# |            This source code is provided under the Apache 2.0 license      --
# |  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
# |                See the project's LICENSE.md for details.                  --
# |           Copyright Refinitiv 2020. All rights reserved.                  --
# |-----------------------------------------------------------------------------

# |-----------------------------------------------------------------------------
# |          Refinitiv Messenger BOT API via HTTP REST and WebSocket          --
# |-----------------------------------------------------------------------------

import sys
import time
import getopt
import requests
import socket
import json
import websocket
import threading
import random
from rdpToken import RDPTokenManagement

# Input your Bot Username
bot_username = 'XXXXX'
# Input Bot Password
bot_password = 'XXXXX'
# Input your Messenger account AppKey.
app_key = 'XXXXX'

# Authentication objects
auth_token = None
rdp_token = None

chatroom_id = None

expire_time = 0
joined_rooms = None

logged_in = False

# Please verify below URL is correct via the WS lookup
ws_url = "wss://api.collab.refinitiv.com/services/nt/api/messenger/v1/stream"


def authen_rdp(rdp_token_object):  # Call RDPTokenManagement to get authentication
    auth_token = rdp_token_object.get_token()
    if auth_token:
        return auth_token, True
    else:
        return None, False
    # return auth_token


# Get List of Chatrooms Function via HTTP REST
def list_chatrooms(access_token, room_is_managed=False):

    if room_is_managed:
        url = 'https://api.refinitiv.com/messenger/beta1/managed_chatrooms'
    else:
        url = 'https://api.refinitiv.com/messenger/beta1/chatrooms'

    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer {}'.format(access_token)}
    response = None
    try:
        # Send a HTTP request message with Python requests module
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print('Messenger BOT API: List Chatroom exception failure:', e)

    if response.status_code == 200:  # HTTP Status 'OK'
        print('Messenger BOT API: get chatroom  success')
    else:
        print('Messenger BOT API: get chatroom result failure:',
              response.status_code, response.reason)
        print('Text:', response.text)

    return response.status_code, response.json()


def join_chatroom(access_token, room_id=None, room_is_managed=False):  # Join chatroom
    joined_rooms = []
    if room_is_managed:
        url = 'https://api.refinitiv.com/messenger/beta1/managed_chatrooms/{}/join'.format(
            room_id)
    else:
        url = 'https://api.refinitiv.com/messenger/beta1/chatrooms/{}/join'.format(
            room_id)

    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer {}'.format(access_token)}

    response = None
    try:
        # Send a HTTP request message with Python requests module
        response = requests.post(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print('Messenger BOT API: join chatroom exception failure:', e)

    if response.status_code == 200:  # HTTP Status 'OK'
        joined_rooms.append(room_id)
        print('Messenger BOT API: join chatroom success')
    else:
        print('Messenger BOT API: join chatroom result failure:',
              response.status_code, response.reason)
        print('Text:', response.text)

    return joined_rooms


# Posting Messages to a Chatroom via HTTP REST
def post_message_to_chatroom(access_token,  joined_rooms, room_id=None,  text='', room_is_managed=False):
    if room_id not in joined_rooms:
        joined_rooms = join_chatroom(access_token, room_id, room_is_managed)

    if joined_rooms:
        if room_is_managed:
            url = 'https://api.refinitiv.com/messenger/beta1/managed_chatrooms/{}/post'.format(
                room_id)
        else:
            url = 'https://api.refinitiv.com/messenger/beta1/chatrooms/{}/post'.format(
                room_id)

        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer {}'.format(access_token)}
        body = {
            "message": text
        }

        response = None
        try:
            response = requests.post(
                url=url, data=json.dumps(body), headers=headers)  # Send a HTTP request message with Python requests module
        except requests.exceptions.RequestException as e:
            print('Messenger BOT API: post message to exception failure:', e)

        if response.status_code == 200:  # HTTP Status 'OK'
            joined_rooms.append(room_id)
            print('Messenger BOT API: post message to chatroom success')
        else:
            print('Messenger BOT API: post message to failure:',
                  response.status_code, response.reason)
            print('Text:', response.text)
    pass


# Leave a joined Chatroom
def leave_chatroom(access_token, joined_rooms, room_id=None, room_is_managed=False):

    if room_id in joined_rooms:
        if room_is_managed:
            url = 'https://api.refinitiv.com/messenger/beta1/managed_chatrooms/{}/leave'.format(
                room_id)
        else:
            url = 'https://api.refinitiv.com/messenger/beta1/chatrooms/{}/leave'.format(
                room_id)

        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer {}'.format(access_token)}

        response = None
        try:
            # Send a HTTP request message with Python requests module
            response = requests.post(url, headers=headers)
        except requests.exceptions.RequestException as e:
            print('Messenger BOT API: leave chatroom exception failure:', e)

        if response.status_code == 200:
            print('Messenger BOT API: leave chatroom success')
        else:
            print('Messenger BOT API: leave chatroom failure:',
                  response.status_code, response.reason)
            print('Text:', response.text)

        joined_rooms.remove(room_id)

    return joined_rooms

# =============================== WebSocket functions ========================================


def on_message(_, message):
    """ Called when message received, parse message into JSON for processing """
    print("RECEIVED: ")
    message_json = json.loads(message)
    print(json.dumps(message_json, sort_keys=True, indent=2, separators=(',', ':')))
    process_message(message_json)


def on_error(_, error):
    """ Called when websocket error has occurred """
    print(error)


def on_close(_):
    """ Called when websocket is closed """
    print("WebSocket Closed")


def on_open(_):
    """ Called when handshake is complete and websocket is open, send login """
    print("WebSocket successfully connected!")
    send_ws_connect_request(auth_token['access_token'])


# Send a connection request to Messenger ChatBot API WebSocket server
def send_ws_connect_request(access_token):
    # set initial point for Python Random module
    random.seed(1)
    # create connection request message in JSON format
    connect_request_msg = {
        'reqId': str(random.randint(0, 1000000)),
        'command': 'connect',
        'payload': {
            'stsToken': access_token
        }
    }
    web_socket_app.send(json.dumps(connect_request_msg))
    print("SENT:")
    print(json.dumps(
        connect_request_msg,
        sort_keys=True,
        indent=2, separators=(',', ':')))


def send_ws_keepalive(access_token):
    # set initial point for Python Random module
    random.seed(1)
    # create connection request message in JSON format
    connect_request_msg = {
        'reqId': str(random.randint(0, 1000000)),
        'command': 'authenticate',
        'payload': {
            'stsToken': access_token
        }
    }
    web_socket_app.send(json.dumps(connect_request_msg))
    print("SENT:")
    print(json.dumps(
        connect_request_msg,
        sort_keys=True,
        indent=2, separators=(',', ':')))


def process_message(message_json):
    #print('Process Message')
    message_event = message_json['event']
    #print('event = ', message_event)
    if message_event == 'chatroomPost':
        try:
            incoming_msg = message_json['post']['message']
            if incoming_msg == "/help" or incoming_msg == "C1" or incoming_msg == "C2" or incoming_msg == "C3":
                post_message_to_chatroom(
                    auth_token['access_token'], joined_rooms, chatroom_id, 'What would you like help with?\n ')
            else:
                print('Receive message = ', incoming_msg)
        except Exception as error:
            print('Post meesage to a Chatroom fail :', error)


# =============================== Main Process ========================================
# Running the tutorial
if __name__ == '__main__':
    print('Getting RDP Authentication Token')

    #print('logged_in = ', logged_in)
    # Create and initiate RDPTokenManagement object
    rdp_token = RDPTokenManagement(bot_username, bot_password, app_key)

    # Authenticate with RDP Token service
    auth_token, logged_in = authen_rdp(rdp_token)
    #print('auth_token, logged_in = authen_rdp(rdp_token) logged_in = ', logged_in)
    if not auth_token:
        sys.exit(1)

    print('Successfully Authenticated ')

    access_token = auth_token['access_token']
    expire_time = auth_token['expires_in']
    # List associated Chatrooms
    print('Get Rooms ')
    status, chatroom_respone = list_chatrooms(access_token)

    # print(json.dumps(chatroom_respone, sort_keys=True,indent=2, separators=(',', ':')))

    chatroom_id = chatroom_respone["chatrooms"][0]["chatroomId"]
    # print('Chatroom ID is ', chatroom_id)

    # Join associated Chatroom
    print('Join Rooms ')
    joined_rooms = join_chatroom(access_token, chatroom_id)
    # print('joined_rooms is ', joined_rooms)

    if not joined_rooms:
        sys.exit(1)

    # Connect to a Chatroom via a WebSocket connection
    print("Connecting to WebSocket %s ... " % (ws_url))
    web_socket_app = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        subprotocols=['messenger-json'])

    web_socket_app.on_open = on_open
    # Event loop
    wst = threading.Thread(
        target=web_socket_app.run_forever,
        kwargs={'sslopt': {'check_hostname': False}})
    wst.start()

    try:
        while True:
            # Give 30 seconds to obtain the new security token and send reissue
            if int(expire_time) > 30:
                time.sleep(int(expire_time) - 30)
            else:
                # Fail the refresh since value too small
                sys.exit(1)
            #sts_token, refresh_token, expire_time = get_sts_token( refresh_token)
            print('Refresh Token ')
            auth_token, logged_in = authen_rdp(rdp_token)
            if not auth_token:
                sys.exit(1)

            # Update token.
            if logged_in:
                send_ws_keepalive(access_token)
    except KeyboardInterrupt:
        web_socket_app.close()
