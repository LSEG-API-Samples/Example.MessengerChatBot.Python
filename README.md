# Messenger Bot API Tutorial
- Last update: January 2020
- Environment: Windows
- Compiler: Python
- Prerequisite: [Access to Eikon Messenger](#prerequisite)

## Introduction

[Eikon Messenger](https://www.refinitiv.com/en/products/eikon-trading-software/eikon-messenger-securemessaging) is a free to use, compliant and secure messaging platform.  It is a powerful communication tool that provides desktop, mobile, and web access, and allows sharing messages, data, files, screenshots, and emoticons with your contacts.

The [Messenger Bot API](https://developers.refinitiv.com/messenger-api) provides a set of available API calls to build automated workflows or bots for Eikon Messenger. The Bot API allows your applications to connect with and pass information into Eikon’s Messenger service programmatically or interact with a bot via a WebSocket connection.

## Table of contents
* [Prerequisite](#prerequisite)
* [Getting the AppKey value](#appkey)
* [Setting the Messenger application](#setting)
* [Running the REST API demo application](#running-rest)
* [Running the WebSocket API demo application](#running-ws)
* [Running demo applications with debug log](#running-debug)
* [Authors](#author)
* [References](#references)

## <a id="prerequisite"></a>Prerequisite 
This tutorial source code requires the following dependencies.
1. [Eikon Messenger](https://www.refinitiv.com/en/products/eikon-trading-software/eikon-messenger-securemessaging).
2. [Python](https://www.python.org/) compiler and runtime
3. Python's [requests 2.x](https://pypi.org/project/requests/) library for both REST and WebSocket connections.
4. Python's [websocket-client](https://pypi.org/project/websocket-client/) library (*version 0.49 or greater*) for the WebSocket connection .
4. Eikon Messenger Bot API access and license.

Please contact your Refinitiv's representative and Dino Diviacchi (dino.diviacchi@refinitiv.com) to help you to access Eikon Message and Bot API. The Refinitiv team will then provision and set up the bot. Once this is done the email user you provided will receive an automated email with how to set up a password for the bot.

*Note:* 
- The Python example has been qualified with Python versions 3.6.5
- Please refer to the [pip installation guide page](https://pip.pypa.io/en/stable/installing/) if your environment does not have the [pip tool](https://pypi.org/project/pip/) installed. 
- If your environment already have a websocket-client library installed, you can use ```pip list``` command to verify a library version, then use ```pip install --upgrade websocket-client``` command to upgrade websocket-client library. 

## <a id="appkey"></a>Getting the AppKey value

Once you have setup your Eikon Messenger user, please access the AppKey Generator Tool via Eikon Desktop/Refinitiv Workspace application (go to the Search Bar and type ```APP KEY```, then select the AppKey Generator) or via a <a href="https://amers1.apps.cp.thomsonreuters.com/apps/AppkeyGenerator">web site</a> (Please access with your Eikon account, *not your bot account*). 

![Figure-1](images/app_key_generator.png "AppKey Generator Tool") 

You can generate your AppKey via the following steps:
1. Enter an App Display Name
2. Select the tick box next to EDP API as the API Type
3. Click ‘Register’ New App button

You will then see a row for your new app with an AppKey item, which is your client_id for the Refinitiv Data Platform (RDP) Authentication. 

## <a id="setting"></a>Setting the Messenger application

Once you have setup your Eikon Messenger user and Bot user, you can add the Bot and create a Chatroom for you and your Bot via the following steps

1. Login to your personal Eikon Messenger to add the bot to your contacts, using “Add a New Contact” from the menu in the lower left corner.

    ![Figure-2](images/eikon_msg_addbot1.png "Add a New Contact") 

2. Add bot name **bot_agent.mybot@refinitiv.com**.

    ![Figure-3](images/eikon_msg_addbot2.png "Add Bot account") 

3. Once you have add the bot it will show up under your contacts (on the left side).

    ![Figure-4](images/eikon_msg_addbot3.png "Your Bot Account") 

4. Create a chatroom using "Create a Bilateral chatroom" button from the menu in the lower left corner.

    ![Figure-5](images/eikon_msg_addbot4.png "Create a chatroom") 

5. Add your Bot to a chatroom by dragging it into your newly created chatroom. 

    ![Figure-6](images/eikon_msg_addbot5.png "Bot Chatroom") 

## <a id="running-rest"></a>Running the REST API demo application
1. Unzip or download the tutorial project folder into a directory of your choice 
2. Run ```$> pip install -r rest-requestments.txt``` command in a console to install all the dependencies libraries.
3. Open the *chatBotAPIPythonREST.py** demo application source code with your editor and input the following parameters
    - ```app_key```: Your AppKey
    - ```bot_username```: Your Bot username
    - ```bot_password```: Your Bot password
    - ```recipient_email``` : Your assoicate Eikon messenger email address 
4. Open a command prompt and folder *src* and run the demo application with the following command.
    ```
    $>python chatBotAPIPythonREST.py
    ```
5. The application then authenticates with [RDP](https://developers.refinitiv.com/refinitiv-data-platform) Authentication service and sends a 1-1 message to your assoicate Eikon message email address. 
    ```
    Getting RDP Authentication Token

    Saving Authentication information to file
    Successfully Authenticated
    send 1 to 1 message to <email>
    Messenger BOT API: post a 1 to 1 message to <email> success
    ```
6. Then a demo gets an associate Chatroom and joining to that Chatroom.
    ```
    Get Rooms
    Messenger BOT API: get chatroom  success
    Join Rooms
    Messenger BOT API: join chatroom success
    ```
7. The demo application will send a default ```Hello from Python``` message to a Chatroom on behalf of the Bot API and lets you send your own message before leaving a Chatroom.
    ```
    sending message to {...} Rooms
    Messenger BOT API: post message to chatroom success
    Please input your message: Wendy, I'm home.
    Messenger BOT API: post message to chatroom success
    Leave Rooms
    Messenger BOT API: leave chatroom success
    ```
## <a id="running-ws"></a>Running the WebSocket API demo application
1. Unzip or download the tutorial project folder into a directory of your choice 
2. Run ```$> pip install -r ws-requestments.txt``` command in a console to install all the dependencies libraries.
3. Open the *chatBotAPIPythonWS.py** demo application source code with your editor and input the following parameters
    - ```app_key```: Your AppKey
    - ```bot_username```: Your Bot username
    - ```bot_password```: Your Bot password
4. Open a command prompt and folder *src* and run the demo application with the following command.
    ```
    $>python chatBotAPIPythonWS.py
    ```
5. The demo will perform authentication process, get an assoicate chatroom, then join that chatroom as same as the REST API demo application [above](#running-rest)
6. Then demo connects to Eikon messenger WebSocket server. Once the application shows WebSocket ```connected``` event in a console, you can start interact with your bot via a chatroom.
    ```
    Messenger BOT API: join chatroom success
    Connecting to WebSocket wss://api.collab.refinitiv.com/services/nt/api/messenger/v1/stream ...
    WebSocket Connection is established
    Sent:....
    Received:
    {
    "event":"connected",
    "reqId":"943378"
    }
    ```
8. Eikon Messenger supports tabular data, hyperlinks and a full set of emoji in the message. You can type ```/complex_message``` message into a Chatroom to see an example.
    ![Figure-7](images/eikon_msg_complex_msg.png "Complex message") 

## <a id="running-debug"></a>Running demo applications with debug log
You can enable the REST and WebSocket application debug log level via ```log_level = logging.WARN``` application source code statement.The supported value is *logging.WARN* and *logging.DEBUG* levels.

The *logging.DEBUG* level show incoming and outgoing messages between the demo applications and Eikon Messenger REST and WebSocket APIs servers.

## <a id="author"></a>Authors
- Wasin Waeosri (wasin.waeosri@refinitiv.com)
- Dino Diviacchi (dino.diviacchi@refinitiv.com)

## <a id="references"></a>References
For further details, please check out the following resources:
* [Refinitiv Messenger Bot API page](https://developers.refinitiv.com/messenger-api) on the [Refinitiv Developer Community](https://developers.refinitiv.com/) web site.
* [Refinitiv Messenger Bot API: Quick Start](https://developers.refinitiv.com/messenger-api/messenger-bot-api/quick-start). 
* [Refinitiv Messenger Bot API: Documentation page](https://developers.refinitiv.com/messenger-api/messenger-bot-api/docs).