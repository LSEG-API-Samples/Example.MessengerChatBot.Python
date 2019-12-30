# |-----------------------------------------------------------------------------
# |            This source code is provided under the Apache 2.0 license      --
# |  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
# |                See the project's LICENSE.md for details.                  --
# |           Copyright Refinitiv 2020. All rights reserved.                  --
# |-----------------------------------------------------------------------------

# |-----------------------------------------------------------------------------
# |                   Refinitiv Messenger BOT API via HTTP REST               --
# |-----------------------------------------------------------------------------

import requests
import json
import sys
from rdpToken import RDPTokenManagement

# Input your Bot Username
bot_username = ''
# Input Bot Password
bot_password = ''
# Input your Messenger account AppKey.
bot_app_key = ''

# Authentication objects
auth_token = None
rdp_token = None

chatroom_id = None


def authen_rdp(rdp_token_object):  # Call RDPTokenManagement to get authentication
    auth_token = rdp_token_object.get_token()
    return auth_token


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
        # Send request message to RDP with Python requests module
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
        # Send request message to RDP with Python requests module
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
                url=url, data=json.dumps(body), headers=headers)
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


# =============================== Main Process ========================================
# Running the tutorial
if __name__ == '__main__':
    print('Getting RDP Authentication Token')

    # Create and initiate RDPTokenManagement object
    rdp_token = RDPTokenManagement(bot_username, bot_password, bot_app_key)

    # Authenticate with RDP Token service
    auth_token = authen_rdp(rdp_token)

    if not auth_token:
        sys.exit(1)

    print('Successfully Authenticated ')

    access_token = auth_token['access_token']

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

    if joined_rooms:
        # Send a default message to a Chatroom
        text_to_post = 'Hello from Python'
        print('sending message to {%s} Rooms ' % (chatroom_id))
        post_message_to_chatroom(
            access_token, joined_rooms, chatroom_id, text_to_post)

        # Receive user input message
        text_input = input('Please input your message: ')
        # Then sends it to a Chatroom
        post_message_to_chatroom(
            access_token, joined_rooms, chatroom_id, text_input)

        print('Leave Rooms ')
        joined_rooms = leave_chatroom(access_token, joined_rooms, chatroom_id)
