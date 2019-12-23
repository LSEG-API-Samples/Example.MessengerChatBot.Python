# =============================================================================
# Refinitiv Data Platform demo app to get OAuth tokens
# =============================================================================
import requests
import json
import time

# User Variables
USERNAME = ""
PASSWORD = ""
CLIENT_ID = ""
UUID = ""					# required for research alerts subscription

# Application Constants
EDP_version = "/v1"
base_URL = "https://api.refinitiv.com"
category_URL = "/auth/oauth2"
endpoint_URL = "/token"
CLIENT_SECRET = ""
TOKEN_FILE = "token.txt"
SCOPE = "trapi.messenger"


TOKEN_ENDPOINT = base_URL + category_URL + EDP_version + endpoint_URL

# =============================================================================


def _requestNewToken(refreshToken):
    if refreshToken is None:
        authenRequest = {
            "username": USERNAME,
            "password": PASSWORD,
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "scope": SCOPE,
            "takeExclusiveSignOnControl": "true"
        }
    else:
        authenRequest = {
            "refresh_token": refreshToken,
            "username": USERNAME,
            "grant_type": "refresh_token",
        }

    # Make a REST call to get latest access token
    response = requests.post(
        TOKEN_ENDPOINT,
        headers={
            "Accept": "application/json"
        },
        data=authenRequest,
        auth=(
            CLIENT_ID,
            CLIENT_SECRET
        )
    )

    if response.status_code != 200:
        raise Exception(
            "Failed to get access token {0} - {1}".format(response.status_code, response.text))

    # Return the new token
    return json.loads(response.text)


# =============================================================================
def changePassword(user, oldPass, clientID, newPass):
    tData = {
        "username": user,
        "password": oldPass,
        "grant_type": "password",
        "scope": SCOPE,
        "takeExclusiveSignOnControl": "true",
        "newPassword": newPass
    }

    # Make a REST call to get latest access token
    response = requests.post(
        TOKEN_ENDPOINT,
        headers={
            "Accept": "application/json"
        },
        data=tData,
        auth=(
            clientID,
            CLIENT_SECRET
        )
    )

    if response.status_code != 200:
        raise Exception(
            "Failed to change password {0} - {1}".format(response.status_code, response.text))

    tknObject = json.loads(response.text)
    # Persist this token for future queries
    saveToken(tknObject)
    # Return access token
    return tknObject["access_token"]


# =============================================================================
def saveToken(tknObject):
    tf = open(TOKEN_FILE, "w")
    print("Saving the new token")
    # Append the expiry time to token
    tknObject["expiry_tm"] = time.time() + int(tknObject["expires_in"]) - 10
    # Store it in the file
    json.dump(tknObject, tf, indent=4)


# =============================================================================
def getToken():
    try:
        print("Reading the token from: " + TOKEN_FILE)
        # Read the token from a file
        tf = open(TOKEN_FILE, "r+")
        tknObject = json.load(tf)

        # Is access token valid
        if tknObject["expiry_tm"] > time.time():
            # return access token
            return tknObject["access_token"]

        print("Token expired, refreshing a new one...")
        tf.close()
        # Get a new token from refresh token
        tknObject = _requestNewToken(tknObject["refresh_token"])

    except:
        print("Getting a new token...")
        tknObject = _requestNewToken(None)

    # Persist this token for future queries
    saveToken(tknObject)
    # Return access token
    return tknObject["access_token"]


# =============================================================================
if __name__ == "__main__":
    # Get latest access token
    print("Getting OAuth access token...")
    accessToken = getToken()
    print("Have token now")
