# =============================================================================
# Refinitiv Data Platform demo app to get OAuth tokens
# =============================================================================

# Import the required libraries for HTTP/JSON operations
import requests
import json
import time

# Authentication Variables

username = ''
password = ''
app_key = ''

# EDP Authentication Service Detail

rdp_authen_version = "/v1"
base_URL = "https://api.refinitiv.com"
category_URL = "/auth/oauth2"
endpoint_URL = "/token"
client_secret = ""
token_file = "./token.txt"
scope = "trapi.messenger"

auth_obj = None

credential_obj = {
    'username': username,
    'password': password,
    'client_id': app_key,
    'client_secret': ''
}

authen_URL = base_URL + category_URL + rdp_authen_version + endpoint_URL


def setCredential(username, password, app_key):
    credential_obj['username'] = username
    credential_obj['password'] = password
    credential_obj['client_id'] = app_key


def requestNewToken(refresh_token):
    if not refresh_token:
        authen_request_msg = {
            "username": credential_obj['username'],
            "password": credential_obj['password'],
            "client_id":  credential_obj['client_id'],
            "grant_type": "password",
            "scope": scope,
            "takeExclusiveSignOnControl": "true"
        }
    else:
        authen_request_msg = {
            "refresh_token": refresh_token,
            "username": username,
            "grant_type": "refresh_token",
        }
    response = None

    try:
        response = requests.post(authen_URL,
                                 headers={'Accept': 'application/json'},
                                 data=authen_request_msg,
                                 auth=(
                                     credential_obj['client_id'],
                                     credential_obj['client_secret']
                                 ))
    except requests.exceptions.RequestException as e:
        print('RDP authentication exception failure:', e)

    if response.status_code == 200:
        print('Authenticaion success')
    else:
        print('RDP authentication result failure:',
              response.status_code, response.reason)
        print('Text:', response.text)
        # both access and refresh tokens are expired
        if response.status_code == 400 and response.json()['error'] == 'invalid_grant':
            print('Both Access Token and Refresh Token are expired')
            raise Exception("Both Access Token and Refresh Token are expired {0} - {1}"
                            .format(response.status_code, response.text))
    return response.status_code, response.json()


def changePassword(username, old_password, client_id, new_password):
    change_password_req_msg = {
        "grant_type": "password",
        "username": username,
        "password": old_password,
        "newPassword": new_password,
        "scope": scope,
        "takeExclusiveSignOnControl": "true"
    }

    try:
        response = requests.post(authen_URL,
                                 headers={'Accept': 'application/json'},
                                 data=authen_request_msg,
                                 auth=(
                                     credential_obj['client_id'],
                                     credential_obj['client_secret']
                                 ))
    except requests.exceptions.RequestException as e:
        print('RDP Change Password exception failure:', e)

    if response.status_code == 200:
        print('Change Password success')
        saveAuthenToFile(response.json())
    else:
        print('RDP Change Password result failure:',
              response.status_code, response.reason)
        print('Text:', response.text)

    return response.status_code, response.json()


def saveAuthenToFile(_authen_obj):
    with open(token_file, 'w') as saved_token:
        print('Saving Authentication information to file')
        _authen_obj['expires_tm'] = time.time(
        ) + int(_authen_obj['expires_in']) - 10
        json.dump(_authen_obj, saved_token, indent=4)


def getToken():
    try:
        with open(token_file, 'r+') as saved_token:
            auth_obj = json.load(saved_token)
            if auth_obj['expires_tm'] > time.time():
                return auth_obj

        print('Token expired, request a new Token with refresh token')
        status, auth_obj = requestNewToken(auth_obj['refresh_token'])
    except IOError as e:
        print(e)
        print('None Token found, requesting a new one')
        status, auth_obj = requestNewToken(None)
    except json.JSONDecodeError as json_error:
        print(json_error)
        print('None Token found, requesting a new one')
        status, auth_obj = requestNewToken(None)
    except:
        print("Getting a new token...")
        status, auth_obj = requestNewToken(None)

    if status == 200:
        saveAuthenToFile(auth_obj)
        return auth_obj
    else:
        return None


# =============================================================================


if __name__ == '__main__':
    print('Getting EDP Authentication Token')

    auth_token = getToken()
    if auth_token:
        print('access token = %s' % auth_token['access_token'])
        print('refresh token = %s' % auth_token['refresh_token'])
        print('expires_in = %s' % auth_token['expires_in'])
