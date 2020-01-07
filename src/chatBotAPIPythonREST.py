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
bot_username = 'XXXXX'
# Input Bot Password
bot_password = 'XXXXX'
# Input your Messenger account AppKey.
app_key = 'XXXXX'
# Input your Eikon Messenger account email
recipient_email = 'XXXXX'

# Authentication objects
auth_token = None
rdp_token = None

chatroom_id = None


def authen_rdp(rdp_token_object):  # Call RDPTokenManagement to get authentication
    auth_token = rdp_token_object.get_token()
    return auth_token['access_token']


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


# send 1 to 1 message to recipient email directly without a Chatroom via BOT
def post_direct_message(access_token, contact_email='', text=''):
    url = 'https://api.refinitiv.com/messenger/beta1/message'

    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer {}'.format(access_token)}

    body = {
        'recipientEmail': contact_email,
        'message': text
    }
    try:
        # Send a HTTP request message with Python requests module
        response = requests.post(
            url=url, data=json.dumps(body), headers=headers)
    except requests.exceptions.RequestException as e:
        print('Messenger BOT API: post a 1 to 1 message exception failure:', e)

    if response.status_code == 200:  # HTTP Status 'OK'
        print('Messenger BOT API: post a 1 to 1 message to %s success' %
              (contact_email))
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
            print('Messenger BOT API: post message exception failure:', e)

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


# =============================== Main Process ========================================
# Running the tutorial
if __name__ == '__main__':
    print('Getting RDP Authentication Token')

    # Create and initiate RDPTokenManagement object
    rdp_token = RDPTokenManagement(bot_username, bot_password, app_key)

    # Authenticate with RDP Token service
    access_token = authen_rdp(rdp_token)

    if not access_token:
        sys.exit(1)

    print('Successfully Authenticated ')

    # Send 1 to 1 message to reipient without a chat room
    text_to_post = """
    USD BBL EU AM Assessment at 11:30 UKT\nName\tAsmt\t10-Apr-19\tFair Value\t10-Apr-19\tHst Cls\nBRT Sw APR19\t70.58\t05:07\t(up) 71.04\t10:58\t70.58\nBRTSw MAY19\t70.13\t05:07\t(dn) 70.59\t10:58\t70.14\nBRT Sw JUN19\t69.75\t05:07\t(up)70.2\t10:58\t69.76
    """
    print('send 1 to 1 message to %s ' % (recipient_email))
    post_direct_message(access_token, recipient_email, text_to_post)

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
