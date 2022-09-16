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
import logging
from rdp_token import RDPTokenManagement

# Input your Bot Username
bot_username = '---YOUR BOT USERNAME---'
# Input Bot Password
bot_password = '---YOUR BOT PASSWORD---'
# Input your Messenger account AppKey.
app_key = '---YOUR MESSENGER ACCOUNT APPKEY---'
# Input your Messenger Application account email
recipient_email = '---YOUR MESSENGER ACCOUNT EMAIL---'
# Setting Log level the supported value is 'logging.INFO' and 'logging.DEBUG'
log_level = logging.DEBUG

# Authentication and connection objectscls
auth_token = None
rdp_token = None
access_token = None
expire_time = 0
logged_in = False

refresh_token = None
# Chatroom objects
chatroom_id = None
joined_rooms = None

# Please verify below URL is correct via the WS lookup
ws_url = 'wss://api.collab.refinitiv.com/services/nt/api/messenger/v1/stream'
gw_url = 'https://api.refinitiv.com'
bot_api_base_path = '/messenger/beta1'

# =============================== RDP and Messenger BOT API functions ========================================


def authen_rdp(rdp_token_object):  # Call RDPTokenManagement to get authentication
    # Based on WebSocket application behavior, the Authentication will not read/write Token from rest-token.txt file
    auth_token = rdp_token_object.get_token(save_token_to_file=False,  current_refresh_token = refresh_token)
    if auth_token:
        # return RDP access token (sts_token) ,refresh_token , expire_in values and RDP login status
        return auth_token['access_token'], auth_token['refresh_token'], auth_token['expires_in'] , True
    else:
        return None,None, 0, False


# Get List of Chatrooms Function via HTTP REST
def list_chatrooms(access_token, room_is_managed=False):

    if room_is_managed:
        url = '{}{}/managed_chatrooms'.format(gw_url, bot_api_base_path)
    else:
        url = '{}{}/chatrooms'.format(gw_url, bot_api_base_path)

    response = None
    try:
        # Send a HTTP request message with Python requests module
        response = requests.get(
            url, headers={'Authorization': 'Bearer {}'.format(access_token)})
    except requests.exceptions.RequestException as e:
        logging.error('Messenger BOT API: List Chatroom exception failure: %s' % e)

    if response.status_code == 200:  # HTTP Status 'OK'
        print('Messenger BOT API: get chatroom  success')
        logging.info('Receive: %s' % (json.dumps(response.json(),sort_keys=True, indent=2, separators=(',', ':'))))
        return response.status_code, response.json()
    else:
        print('Messenger BOT API: get chatroom result failure:',response.status_code, response.reason)
        print('Text:', response.text)
        return response.status_code, None
    


def join_chatroom(access_token, room_id=None, room_is_managed=False):  # Join chatroom
    joined_rooms = []
    if room_is_managed:
        url = '{}{}/managed_chatrooms/{}/join'.format(
            gw_url, bot_api_base_path, room_id)
    else:
        url = '{}{}/chatrooms/{}/join'.format(gw_url,
                                              bot_api_base_path, room_id)

    response = None
    try:
        # Send a HTTP request message with Python requests module
        response = requests.post(
            url, headers={'Authorization': 'Bearer {}'.format(access_token)})
    except requests.exceptions.RequestException as e:
        logging.error('Messenger BOT API: join chatroom exception failure: %s' % e)

    if response.status_code == 200:  # HTTP Status 'OK'
        joined_rooms.append(room_id)
        print('Messenger BOT API: join chatroom success')
        logging.info('Receive: %s' % (json.dumps(response.json(),sort_keys=True, indent=2, separators=(',', ':'))))
    else:
        print('Messenger BOT API: join chatroom result failure:',
              response.status_code, response.reason)
        print('Text:', response.text)

    return joined_rooms


# send 1 to 1 message to recipient email directly without a Chatroom via BOT
def post_direct_message(access_token, contact_email='', text=''):
    url = '{}{}/message'.format(gw_url, bot_api_base_path)

    body = {
        'recipientEmail': contact_email,
        'message': text
    }

    # Print for debugging purpose
    logging.info('Sent: %s' % (json.dumps(body, sort_keys=True, indent=2, separators=(',', ':'))))

    try:
        # Send a HTTP request message with Python requests module
        response = requests.post(
            url=url, data=json.dumps(body), headers={'Authorization': 'Bearer {}'.format(access_token)})
    except requests.exceptions.RequestException as e:
        logging.error('Messenger BOT API: post a 1 to 1 message exception failure: %s ' % e)

    if response.status_code == 200:  # HTTP Status 'OK'
        print('Messenger BOT API: post a 1 to 1 message to %s success' %
              (contact_email))
        logging.info('Receive: %s' % (json.dumps(response.json(),sort_keys=True, indent=2, separators=(',', ':'))))
    else:
        print('Messenger BOT API: post a 1 to 1 message failure:',
              response.status_code, response.reason)
        print('Text:', response.text)


# Posting Messages to a Chatroom via HTTP REST
def post_message_to_chatroom(access_token,  joined_rooms, room_id=None,  text='', room_is_managed=False):
    if room_id not in joined_rooms:
        joined_rooms = join_chatroom(access_token, room_id, room_is_managed)

    if joined_rooms:
        if room_is_managed:
            url = '{}{}/managed_chatrooms/{}/post'.format(
                gw_url, bot_api_base_path, room_id)
        else:
            url = '{}{}/chatrooms/{}/post'.format(
                gw_url, bot_api_base_path, room_id)

        body = {
            'message': text
        }

        # Print for debugging purpose
        logging.info('Sent: %s' % (json.dumps(body, sort_keys=True, indent=2, separators=(',', ':'))))

        response = None
        try:
            # Send a HTTP request message with Python requests module
            response = requests.post(
                url=url, data=json.dumps(body), headers={'Authorization': 'Bearer {}'.format(access_token)})
        except requests.exceptions.RequestException as e:
            logging.error('Messenger BOT API: post message to exception failure: %s ' % e)

        if response.status_code == 200:  # HTTP Status 'OK'
            joined_rooms.append(room_id)
            print('Messenger BOT API: post message to chatroom success')
            # Print for debugging purpose
            logging.info('Receive: %s' % (json.dumps(
                response.json(), sort_keys=True, indent=2, separators=(',', ':'))))
        else:
            print('Messenger BOT API: post message to failure:',
                  response.status_code, response.reason)
            print('Text:', response.text)
    pass


# Leave a joined Chatroom
def leave_chatroom(access_token, joined_rooms, room_id=None, room_is_managed=False):

    if room_id in joined_rooms:
        if room_is_managed:
            url = '{}{}/managed_chatrooms/{}/leave'.format(
                gw_url, bot_api_base_path, room_id)
        else:
            url = '{}{}/chatrooms/{}/leave'.format(
                gw_url, bot_api_base_path, room_id)

        response = None
        try:
            # Send a HTTP request message with Python requests module
            response = requests.post(
                url, headers={'Authorization': 'Bearer {}'.format(access_token)})
        except requests.exceptions.RequestException as e:
            logging.error('Messenger BOT API: leave chatroom exception failure: %s' % e)

        if response.status_code == 200:  # HTTP Status 'OK'
            print('Messenger BOT API: leave chatroom success')
            logging.info('Receive: %s' % (json.dumps(response.json(), sort_keys=True, indent=2, separators=(',', ':'))))
        else:
            print('Messenger BOT API: leave chatroom failure:',
                  response.status_code, response.reason)
            print('Text:', response.text)

        joined_rooms.remove(room_id)

    return joined_rooms

# =============================== WebSocket functions ========================================


def on_message(_, message):  # Called when message received, parse message into JSON for processing
    message_json = json.loads(message)
    logging.debug('Received: %s' % (json.dumps(message_json, sort_keys=True, indent=2, separators=(',', ':'))))
    process_message(message_json)


def on_error(_, error):  # Called when websocket error has occurred
    logging.error('Error: %s' % (error))


def on_close(_, close_status_code, close_msg):  # Called when websocket is closed
    logging.error('Receive: onclose event. WebSocket Connection Closed')
    leave_chatroom(access_token, joined_rooms, chatroom_id)
    # Abort application
    sys.exit("Abort application")


def on_open(_):  # Called when handshake is complete and websocket is open, send login
    logging.info('Receive: onopen event. WebSocket Connection is established')
    send_ws_connect_request(access_token)

# For the environment that needs a ping-pong message only
def on_ping(_, message):
    print("Got a ping! A pong reply has already been automatically sent.")

# For the environment that needs a ping-pong message only
def on_pong(_, message):
    print("Got a pong! No need to respond")


# Send a connection request to Messenger ChatBot API WebSocket server
def send_ws_connect_request(access_token):

    # create connection request message in JSON format
    connect_request_msg = {
        'reqId': str(random.randint(0, 1000000)),
        'command': 'connect',
        'payload': {
            'stsToken': access_token
        }
    }
    try:
        web_socket_app.send(json.dumps(connect_request_msg))
    except Exception as error:
        #print('send_ws_connect_request Exception:', error)
        logging.error('send_ws_connect_request exception: %s' % (error))

    logging.info('Sent: %s' % (json.dumps(connect_request_msg, sort_keys=True, indent=2, separators=(',', ':'))))


# Function for Refreshing Tokens.  Auth Tokens need to be refreshed within 5 minutes for the WebSocket to persist
def send_ws_keepalive(access_token):

    # create connection request message in JSON format
    connect_request_msg = {
        'reqId': str(random.randint(0, 1000000)),
        'command': 'authenticate',
        'payload': {
            'stsToken': access_token
        }
    }
    try:
        web_socket_app.send(json.dumps(connect_request_msg))
    except Exception as error:
        #print('send_ws_connect_request Exception :', error)
        logging.error('send_ws_connect_request exception: %s' % (error))
    
    logging.info('Sent: %s' % (json.dumps(connect_request_msg, sort_keys=True, indent=2, separators=(',', ':'))))


def process_message(message_json):  # Process incoming message from a joined Chatroom

    message_event = message_json['event']

    if message_event == 'chatroomPost':
        try:
            incoming_msg = message_json['post']['message']
            print('Receive text message: %s' % (incoming_msg))
            if incoming_msg == '/help' or incoming_msg == 'C1' or incoming_msg == 'C2' or incoming_msg == 'C3':
                post_message_to_chatroom(
                    access_token, joined_rooms, chatroom_id, 'What would you like help with?\n ')
            # Sending tabular data, hyperlinks and a full set of emoji in a message to a Chatroom
            elif incoming_msg.lower() == '/complex_message':
                complex_msg = """
                USD BBL EU AM Assessment at 11:30 UKT\nName\tAsmt\t10-Apr-19\tFair Value\t10-Apr-19\tHst Cls\nBRT Sw APR19\t70.58\t05:07\t(up) 71.04\t10:58\t70.58\nBRTSw MAY19\t70.13\t05:07\t(dn) 70.59\t10:58\t70.14\nBRT Sw JUN19\t69.75\t05:07\t(up)70.2\t10:58\t69.76
                """
                post_message_to_chatroom(
                    access_token, joined_rooms, chatroom_id, complex_msg)
            # Receive 'Hello' message, get sender email address and say hello back
            elif incoming_msg.lower() == 'hello':
                sender = message_json['post']['sender']['email']
                post_message_to_chatroom(
                    access_token, joined_rooms, chatroom_id, 'Hello %s\n ' % (sender))

        except Exception as error:
            logging.error('Post meesage to a Chatroom fail : %s' % error)


# =============================== Main Process ========================================
# Running the tutorial
if __name__ == '__main__':

    # Setting Python Logging
    logging.basicConfig(format='%(asctime)s: %(levelname)s:%(name)s :%(message)s', level=log_level, datefmt='%Y-%m-%d %H:%M:%S')

    print('Getting RDP Authentication Token')

    # Create and initiate RDPTokenManagement object
    rdp_token = RDPTokenManagement(bot_username, bot_password, app_key, 30)

    # Authenticate with RDP Token service
    access_token, refresh_token, expire_time, logged_in = authen_rdp(rdp_token)
    # if not auth_token:
    if not access_token:
        # Abort application
        sys.exit(1)

    print('Successfully Authenticated ')

    # Send 1 to 1 message to reipient without a chat room
    print('send 1 to 1 message to %s ' % (recipient_email))
    post_direct_message(access_token, recipient_email, 'Hello from Python')

    # List associated Chatrooms
    print('Get Rooms ')
    status, chatroom_respone = list_chatrooms(access_token)

    if not chatroom_respone:
        # Abort application
        sys.exit(1)

    #print(json.dumps(chatroom_respone, sort_keys=True,indent=2, separators=(',', ':')))

    chatroom_id = chatroom_respone['chatrooms'][0]['chatroomId']
    # print('Chatroom ID is ', chatroom_id)

    # Join associated Chatroom
    print('Join Rooms ')
    joined_rooms = join_chatroom(access_token, chatroom_id)
    # print('joined_rooms is ', joined_rooms)

    if not joined_rooms:
        # Abort application
        sys.exit(1)

    # Connect to a Chatroom via a WebSocket connection
    print('Connecting to WebSocket %s ... ' % (ws_url))
    #websocket.enableTrace(True)
    web_socket_app = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
        subprotocols=['messenger-json'])
    # Event loop
    wst = threading.Thread(
        target=web_socket_app.run_forever,
        kwargs={'sslopt': {'check_hostname': False}})
    
    # # For the environment that needs a ping-pong message only
    # web_socket_app = websocket.WebSocketApp(ws_url,
    #     on_message=on_message,
    #     on_error=on_error,
    #     on_close=on_close,
    #     on_open=on_open,
    #     on_ping=on_ping,
    #     on_pong=on_pong,
    #     subprotocols=['messenger-json'])
    # # Event loop
    # wst = threading.Thread(target=web_socket_app.run_forever, kwargs={"sslopt": {"check_hostname": False}, "ping_interval": 60, "ping_timeout": 10, "ping_payload": "2"})

    wst.start()

    try:
        while True:
            # Give 60 seconds to obtain the new security token and send reissue
            #logging.debug('expire_time = %s' %(expire_time))
            if int(expire_time) > 60: 
                #The current RDP expires_time is 600 seconds (10 minutes). However, the Messenger Bot WebSocket server still uses 300 seconds (5 minutes).
                expire_time = '300'
                time.sleep(int(expire_time) - 60) 
            else:
                # Fail the refresh since value too small
                # Abort application
                sys.exit(1)

            print('Refresh Token ')
            access_token, refresh_token, expire_time, logged_in = authen_rdp(rdp_token)
            if not access_token:
                # Abort application
                sys.exit(1)
            # Update authentication token to the WebSocket connection.
            if logged_in:
                send_ws_keepalive(access_token)
    except KeyboardInterrupt:
        web_socket_app.close()
