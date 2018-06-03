# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../ft')

import os
from flask import Flask, request
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
import requests, json
from pymongo import MongoClient
import facebook
from datetime import datetime, timezone
import time
import random
import ft_functions
from keys import DF_TOKEN, GOOGLE_MAPS_API_KEY, MAIL_PWD, FB_ACCESS_TOKEN, FB_VERIFY_TOKEN
from translations import L10N

app = Flask(__name__)
graph = facebook.GraphAPI(access_token=FB_ACCESS_TOKEN, version="2.2")

mail = Mail(app)
app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME = 'mailvulgaris@gmail.com',
    MAIL_PASSWORD = MAIL_PWD
)
mail = Mail(app)

'''
    Plain text input and callbacks from button clicks (persistent menu, templates with buttons) are passed for NLU
    to Dialogflow. Responses and intents returned from DF together with contexts are used to handle dialog flow

    Persistent menu:
    1. Start (what's this is all about, traveler's story) 
    2. Help/Settings
        |- 2.1 Get help
        |- 2.2 Change language
    3. If you got a fellow traveler
'''

####################################### FBM Bot INI START #######################################

OURTRAVELLER = 'Teddy'
PHOTO_DIR = '../ft/static/uploads/{}/'.format(OURTRAVELLER) # where photos from places visited are saved
SERVICE_IMG_DIR = '../ft/static/uploads/{}/service/'.format(OURTRAVELLER) # where 'general info' images are saved (summary map, secret code example etc)
SHORT_TIMEOUT = 1  # 2 # seconds, between messages for imitation of 'live' typing
MEDIUM_TIMEOUT = 2  # 4
LONG_TIMEOUT = 3  # 6
SUPPORT_EMAIL = 'iurii.dziuban@gmail.com'
USER_LANGUAGE = 'en'#None

CONTEXTS = []   # holds last state
NEWLOCATION = {    # holds data for traveler's location before storing it to DB
    'author': None,
    'channel': 'Facebook',
    'user_id_on_channel': None,
    'longitude': None,
    'latitude': None,
    'formatted_address': None,
    'locality': None,
    'administrative_area_level_1': None,
    'country': None,
    'place_id': None,
    'comment': None,
    'photos': []
}

LANGUAGES = {
    'en': 'English',
    'ru': 'Русский',
    #'de': 'Deutsch',
    #'fr': 'Français',
    'uk': 'Українська'
}
####################################### FBM Bot INI END #########################################

########################################## Functions START ######################################


def get_language(user_id):
    '''
        Retrieves user locale using Facebook Graph API for a user with user_id
    '''
    locale = graph.get_object(id=str(user_id), fields='locale') # {'id': '19xxxxxxxxxxx052', 'locale': 'en_GB'}
    language = 'en'
    if locale.get('locale'):
        if locale.get('locale') == 'uk_UA':
            language = 'uk'
        elif locale.get('locale') == 'ru_RU':
            language = 'ru'
    return language


def send_message(user_id, our_message):
    '''
    Sends a our_message to FB user with recipient_id
    '''
    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                        params = {'access_token': FB_ACCESS_TOKEN},
                        data = json.dumps(
                            {
                                'recipient': {'id': user_id},
                                'message': our_message
                            }
                        ),
                        headers={'Content-type': 'application/json'}
                      )
    if r.status_code != requests.codes.ok:
        print(r.text)


def travelers_story_intro(user_id):
    '''
        Traveler presents him/herself, his/her goal and asks if user would like to know more about traveler's journey
    '''
    # message57 = 'My name is'
    # message58 = 'I\'m a traveler.\nMy dream is to see the world'
    print(L10N['message57'][USER_LANGUAGE])
    print(OURTRAVELLER)
    send_message(user_id, my_name_is_ch_language)
    time.sleep(SHORT_TIMEOUT)
    # message59 = 'Do you want to know more about my journey?'
    send_message(user_id, want_my_journey)


############################################ Functions END #######################################

########################################### Templates START ######################################

# Generic template - photo of traveler with button "Change language"
my_name_is_ch_language = {
    "attachment":{
          "type":"template",
          "payload":{
            "template_type":"generic",
            "elements":[
               {
                # message57 = 'My name is'
                "title":'{} {}'.format(L10N['message57'][USER_LANGUAGE], OURTRAVELLER),
                "image_url":"https://fellowtraveler.club/static/uploads/Teddy/service/Teddy.jpg", #open(SERVICE_IMG_DIR + OURTRAVELLER + '.jpg', 'rb')
                # message58 = 'I\'m a traveler.\nMy dream is to see the world'
                "subtitle":L10N['message58'][USER_LANGUAGE],
                "buttons":[
                    {
                        "type": "postback",
                        # message83 = "Change language"
                        "title": L10N['message83'][USER_LANGUAGE],
                        "payload": "CHANGE_LANGUAGE",
                  }
                ]
              }
            ]
          }
        }
}

# Button template - 'Do you want to know more about my journey?' Yes/No
want_my_journey = {
    "attachment":{
          "type":"template",
          "payload":{
            "template_type":"button",
            # message59 = 'Do you want to know more about my journey?'
            "text":L10N['message59'][USER_LANGUAGE],
            "buttons":[
              {
                    "type":"postback",
                    # message47 = "Yes"
                    "title":L10N['message47'][USER_LANGUAGE],
                    "payload":L10N['message47'][USER_LANGUAGE]
              },
                {
                    "type": "postback",
                    # message48 = "No, thanks"
                    "title": L10N['message48'][USER_LANGUAGE],
                    "payload": L10N['message48'][USER_LANGUAGE]
                }
            ]
          }
        }
}
############################################ Templates END #######################################

################### Handlers for Persistent Menu clicks - START ##################################

# Block 0
def getting_started(user_id):
    global CONTEXTS
    global USER_LANGUAGE
    # A fix intended not to respond to every image uploaded (if several)
    ##respond_to_several_photos_only_once()

    # Get user language from message
    if not USER_LANGUAGE:
        USER_LANGUAGE = get_language(user_id)

    if 'if_journey_info_needed' not in CONTEXTS:
        CONTEXTS.clear()
        user_first_name = graph.get_object(id=str(user_id), fields='first_name') # {'id': '19xxxxxxxxxxx052', 'first_name': 'Iurii'}
        if not user_first_name.get('first_name'):
            user_name =''
        else:
            user_name = ', {}'.format(user_first_name.get('first_name'))
        # message0 = 'Hello'
        send_message(user_id, '{}, {}!'.format(L10N['message0'][USER_LANGUAGE], user_name))
        CONTEXTS.append('if_journey_info_needed')
        time.sleep(SHORT_TIMEOUT)

    travelers_story_intro(user_id)

    # Console logging
    print()
    print('User clicked "Start" in Persistent menu')
    print('Contexts: {}'.format(CONTEXTS))

#################### Handlers for Persistent Menu clicks - END ###################################


@app.route("/")
def index():
    return "<h1 style='color:blue'>FB Messenger Bot for fellowtraveler.club</h1>"

@app.route("/webhook/", methods=['GET', 'POST'])
def message_webhook():
    print("\nrequest.args: ")
    print(request.args)

    if request.method == 'GET':
        print('\nGET request')
        if request.args.get("hub.verify_token") == FB_VERIFY_TOKEN:
            print('Verified!')
            return request.args.get("hub.challenge"), 200
        else:
            return 'Invalid verification token', 403

    if request.method == 'POST':
        print('\nPOST request')

        output = request.get_json()

        print("\nrequest.get_json(): ")
        print(output)

        if output.get('object') == 'page':
            for entry in output.get('entry'):
                if entry.get('messaging'):
                    for message in entry.get('messaging'):
                        if message.get('message'):
                            sender_id = message.get('sender').get('id')

                            # Text messages (emoji also get here)
                            if message.get('message').get('text') and not message.get('message').get('is_echo'):
                                user_wrote = message.get('message').get('text').encode('unicode_escape')
                                send_message(sender_id, {'text': 'You said "{}'.format(user_wrote.decode('unicode_escape'))})

                            # Button clicks
                            if message.get('postback') and message.get('postback').get('payload'):
                                button_postback = message.get('postback').get('payload')
                                # Two main cases:
                                # 1. Persistent menu buttons
                                if button_postback == 'GETTING_STARTED':
                                    getting_started(sender_id)
                                elif button_postback == 'START_TRIGGER':
                                    pass
                                elif button_postback == 'GET_HELP':
                                    pass
                                elif button_postback == 'CHANGE_LANGUAGE':
                                    pass
                                elif button_postback == 'YOU_GOT_FELLOW_TRAVELER':
                                    pass
                                # 2. All other buttons
                                else:
                                    pass

                            # Attachments
                            if message.get('message').get('attachments'):
                                for attachment in message.get('message').get('attachments'):
                                    # Images (photos from camera, gifs, likes also get here)
                                    if attachment.get('type') == 'image' and not attachment.get('payload').get('sticker_id'):
                                        send_message(sender_id, {'text': 'Img url "{}'.format(attachment.get('payload').get('url'))})

                                    # Location
                                    elif attachment.get('type') == 'location':
                                        latitude = attachment.get('payload').get('coordinates').get('lat')
                                        longitude = attachment.get('payload').get('coordinates').get('long')

                                    # Other content types - audio, file, stickers (as images but with field 'sticker_id')
                                    else:
                                        print('Other content types')
        return "Success", 200

if __name__ == "__main__":
    print('\nFB Messenger Bot - new session\n')
    app.run(host='0.0.0.0', port=5000)
