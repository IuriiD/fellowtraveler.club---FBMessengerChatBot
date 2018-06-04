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
import ft_functions # common for the web version and chatbots
import fft_functions # specific for chatbot for FB Messenger
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
USER_LANGUAGE = 'en'

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


def get_user_firt_name(user_id):
    '''
        Retrieves user first name using Facebook Graph API for a user with user_id
    '''
    user_first_name = graph.get_object(id=str(user_id),
                                       fields='first_name')  # {'id': '19xxxxxxxxxxx052', 'first_name': 'Iurii'}
    if user_first_name.get('first_name'):
        return user_first_name.get('first_name')
    else:
        return False


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


def send_text_message(user_id, text):
    '''
    Sends a text message (text) to FB user with recipient_id
    '''
    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                        params = {'access_token': FB_ACCESS_TOKEN},
                        data = json.dumps(
                            {
                                'recipient': {'id': user_id},
                                'message': {'text': text}
                            }
                        ),
                        headers={'Content-type': 'application/json'}
                      )
    if r.status_code != requests.codes.ok:
        print(r.text)


def send_generic_template_message(user_id, title, subtitle='', image_url='', buttons=[]):
    '''
    Sends a generic message (with title, subtitle[optional], image uploaded from url[optional] and up to 3 buttons)
    to FB user with recipient_id
    Buttons of 'postback' type, title=payload
    '''
    our_buttons = []
    for button in buttons:
        our_buttons.append(
            {
                'type': 'postback',
                'title': button['title'],
                'payload': button['payload']
            }
        )

    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                        params = {'access_token': FB_ACCESS_TOKEN},
                        data = json.dumps(
                            {
                                'recipient': {'id': user_id},
                                'message': {
                                    'attachment': {
                                        'type': 'template',
                                        'payload': {
                                            'template_type': 'generic',
                                            'elements': [
                                                {
                                                    'title': title,
                                                    'image_url': image_url,
                                                    'subtitle': subtitle,
                                                    'buttons': our_buttons
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ),
                        headers={'Content-type': 'application/json'}
                      )
    if r.status_code != requests.codes.ok:
        print(r.text)


def send_button_template_message(user_id, text, buttons=[]):
    '''
    Sends a button template message (text + up to 3 buttons) to FB user with recipient_id
    Buttons of 'postback' type
    '''
    our_buttons = []
    for button in buttons:
        our_buttons.append(
            {
                'type': 'postback',
                'title': button['title'],
                'payload': button['payload']
            }
        )

    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                        params = {'access_token': FB_ACCESS_TOKEN},
                        data = json.dumps(
                            {
                                'recipient': {'id': user_id},
                                'message': {
                                    'attachment': {
                                        'type': 'template',
                                        'payload': {
                                            'template_type': 'button',
                                            'text': text,
                                            'buttons': our_buttons
                                        }
                                    }
                                }
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
    print('Hello from travelers_story_intro()')

    # message57 = 'My name is'
    message1 = '{} {}'.format(L10N['message57'][USER_LANGUAGE], OURTRAVELLER)
    # message58 = 'I\'m a traveler.\nMy dream is to see the world'
    message2 = L10N['message58'][USER_LANGUAGE]

    print('\nSending the 1st message with text {} - {}'.format(message1, message2))

    send_generic_template_message(user_id,
                                    title=message1,
                                    subtitle=message2,
                                    image_url='https://fellowtraveler.club/static/uploads/Teddy/service/Teddy.jpg',
                                    buttons=[
                                        {
                                           'type': 'postback',
                                           # message83 = "Change language"
                                           'title': L10N['message83'][USER_LANGUAGE],
                                           'payload': 'CHANGE_LANGUAGE'
                                        }
                                    ]
                                  )
    time.sleep(SHORT_TIMEOUT)




    # message59 = 'Do you want to know more about my journey?'
    message3 = L10N['message59'][USER_LANGUAGE]

    send_button_template_message(user_id, text=message3, buttons=[
        {
            'type': 'postback',
            # message47 = "Yes"
            'title': L10N['message47'][USER_LANGUAGE],
            'payload': L10N['message47'][USER_LANGUAGE]
        },
        {
            'type': 'postback',
            # message48 = "No, thanks"
            'title': L10N['message48'][USER_LANGUAGE],
            'payload': L10N['message48'][USER_LANGUAGE]
        },
    ])


def get_help(user_id):
    '''
        Displays FAQ/help
    '''
    global CONTEXTS

    CONTEXTS.clear()
    # message80 = 'Here\'s our FAQ'
    send_text_message(user_id, L10N['message80'][USER_LANGUAGE])


    send_button_template_message(user_id,
                                 # message8 = 'What would you like to do next?
                                 text=L10N['message8'][USER_LANGUAGE],
                                 buttons=[
        {
            # message99 = "Start"
            "title": L10N['message99'][USER_LANGUAGE],
            "payload": 'START_TRIGGER'
        },
        {
             # message45 = "FAQ"
             "title": L10N['message45'][USER_LANGUAGE],
             "payload": L10N['message45'][USER_LANGUAGE]
        },
        {
            # message46 = "You got"
            # message85 = "You got fellowtraveler"
            "title": '{} {}?'.format(L10N['message46'][USER_LANGUAGE], OURTRAVELLER),
            "payload": L10N['message85'][USER_LANGUAGE]
        }
    ])


def getting_started(user_id):
    '''
        User clicks either 'Getting started' button when launching the bot or button 'Start' from Persistent menu
    '''
    global CONTEXTS
    global USER_LANGUAGE

    print('CONTEXTS at function entry: {}'.format(CONTEXTS))
    # A fix intended not to respond to every image uploaded (if several)
    ##respond_to_several_photos_only_once()

    # Get user language from message
    if not USER_LANGUAGE:
        USER_LANGUAGE = get_language(user_id)

    if 'if_journey_info_needed' not in CONTEXTS:
        CONTEXTS.clear()

        first_name = get_user_firt_name(user_id)
        user_name = ''
        if first_name:
            user_name = ', {}'.format(first_name)

        # message0 = 'Hello'
        message = '{}{}!'.format(L10N['message0'][USER_LANGUAGE], user_name)
        send_text_message(user_id, message)
        CONTEXTS.append('if_journey_info_needed')
        time.sleep(SHORT_TIMEOUT)

    travelers_story_intro(user_id)

    # Console logging
    print()
    print('User clicked button "Help/Settings >> Get help" in Persistent menu')
    print('Contexts at function exit: {}'.format(CONTEXTS))


def help(user_id):
    '''
        User clicks button 'Help/Settings' >> 'Get help' in Persistent menu
    '''
    global CONTEXTS
    print('CONTEXTS at function entry: {}'.format(CONTEXTS))
    # A fix intended not to respond to every image uploaded (if several)
    ##respond_to_several_photos_only_once()

    get_help(user_id)

    # Console logging
    print()
    print('User clicked "Help/Settings >> Get help" in Persistent menu')
    print('Contexts at function exit: {}'.format(CONTEXTS))


def you_got_fellowtraveler(user_id):
    '''
        User clicked button 'If you got a fellow traveler' in Persistent menu
    '''
    global CONTEXTS
    # A fix intended not to respond to every image uploaded (if several)
    ##respond_to_several_photos_only_once()

    if 'code_correct' not in CONTEXTS:
        # message1 = 'Congratulations! That\'s a tiny adventure and some responsibility ;)'
        message1 = L10N['message1'][USER_LANGUAGE]
        send_text_message(user_id, message1)

        # message60 = 'To proceed please enter the secret code from the toy'
        message2 = L10N['message60'][USER_LANGUAGE]
        send_generic_template_message(user_id,
                                      title=message2,
                                      image_url='https://fellowtraveler.club/static/uploads/Teddy/service/how_secret_code_looks_like.jpg',
                                      buttons=[
                                          {
                                              # message50 = "Cancel"
                                              "title": L10N['message50'][USER_LANGUAGE],
                                              "payload": L10N['message50'][USER_LANGUAGE]
                                          },
                                          {
                                              # message45 = "FAQ"
                                              "title": L10N['message45'][USER_LANGUAGE],
                                              "payload": L10N['message45'][USER_LANGUAGE]
                                          },
                                          {
                                              # message51 = "Contact support"
                                              "title": L10N['message51'][USER_LANGUAGE],
                                              "payload": L10N['message51'][USER_LANGUAGE]
                                          }
                                      ]
                                      )

    else:
        # message6 = 'Ok'
        # message8 = 'What would you like to do next?'
        message3 = '{}. {}'.format(L10N['message6'][USER_LANGUAGE], L10N['message8'][USER_LANGUAGE])
        send_button_template_message(user_id,
                                     text=message3,
                                     buttons=[
                                         {
                                             # message52 = "Instructions"
                                             "title": L10N['message52'][USER_LANGUAGE],
                                             "payload": L10N['message52'][USER_LANGUAGE]
                                         },
                                         {
                                             # message53 = "Add location"
                                             "title": L10N['message53'][USER_LANGUAGE],
                                             "payload": L10N['message53'][USER_LANGUAGE]
                                         },
                                         {
                                             # message51 = "Contact support"
                                             "title": L10N['message51'][USER_LANGUAGE],
                                             "payload": L10N['message51'][USER_LANGUAGE]
                                         }
                                     ]
                                     )

    # Console logging
    print()
    print('User clicked button "If you got a fellow traveler" in Persistent menu')
    print('Contexts: {}'.format(CONTEXTS))


def change_language(user_id):
    '''
        User clicked button 'Change language' in Persistent menu
    '''
    global USER_LANGUAGE

    if not USER_LANGUAGE:
        USER_LANGUAGE = get_language(user_id)

    # message81 = 'Please select your language'
    message = L10N['message81'][USER_LANGUAGE]
    send_button_template_message(user_id,
                                 text=message,
                                 buttons=[
                                     {
                                         # message86 = 'Change language to English'
                                         "title": 'English',
                                         "payload": L10N['message86'][USER_LANGUAGE]
                                     },
                                     {
                                         # message87 = 'Change language to Russian'
                                         "title": 'Русский',
                                         "payload": L10N['message87'][USER_LANGUAGE]
                                     },
                                     {
                                         # message88 = 'Change language to Ukrainian'
                                         "title": 'Українська',
                                         "payload": L10N['message88'][USER_LANGUAGE]
                                     }
                                 ]
                                 )

    print()
    print('User entered "/change_language"')
    print('Contexts: {}'.format(CONTEXTS))


def text_handler(user_id, from_user, message):
    '''
        Handling all text input (NLP using Dialogflow and then depending on recognised intent and contexts variable
    '''
    global CONTEXTS
    global USER_LANGUAGE
    # A fix intended not to respond to every image uploaded (if several)
    ##respond_to_several_photos_only_once()

    # Get input data
    users_input = message
    chat_id = user_id

    if USER_LANGUAGE == None:
        USER_LANGUAGE = get_language(user_id)

    # And pass it to the main handler function [main_hadler()]
    main_handler(users_input, chat_id, from_user, is_btn_click=False, geodata=None, media=False, other_input=False)


def button_click_handler(user_id, from_user, button_payload):
    '''
        Handling clicks on buttons (except for Persistent menu and 'Getting started')

        All possible buttons (10)
        Yes | No, thanks | Cancel | Help | You got Teddy? | Teddy's story | Next | Contact support | Instructions | Add location
        Buttons | Instructions | Add location | are available only after entering secret code
        Buttons | You got Teddy? | Teddy's story | Help | Contact Support | are activated irrespective of context,
        Buttons | Instructions | Add location | are activated always in context 'code_correct',
        other buttons ( Yes | No, thanks | Cancel | Next) - depend on context, if contexts==[] or irrelevant context - they
        should return a response for a Fallback_Intent
    '''
    global CONTEXTS
    global USER_LANGUAGE
    # A fix intended not to respond to every image uploaded (if several)
    #respond_to_several_photos_only_once()

    # Get input data
    users_input = button_payload
    chat_id = user_id

    # Get user language from message
    if not USER_LANGUAGE:
        USER_LANGUAGE = get_language(user_id)

    # And pass it to the main handler function [main_hadler()]
    main_handler(users_input, chat_id, from_user, is_btn_click=True, geodata=None, media=False, other_input=False)


def location_handler(user_id, from_user, lat, long):
    '''
        Handling location input
    '''
    global CONTEXTS
    global NEWLOCATION
    global USER_LANGUAGE
    # A fix intended not to respond to every image uploaded (if several)
    #respond_to_several_photos_only_once()

    # Get input data
    users_input = 'User posted location'
    chat_id = user_id

    if USER_LANGUAGE == None:
        USER_LANGUAGE = USER_LANGUAGE = get_language(user_id)

    # And pass it to the main handler function [main_hadler()]
    main_handler(users_input, chat_id, from_user, is_btn_click=False, geodata={'lat': lat, 'lng': long}, media=False, other_input=False)


def photo_handler(user_id, from_user, img_url):
    '''
        Looks like in FB as distinct from Telegram several images sent by user come in one message (though in separate
        dictionaries inside of entry[x].messaging[y].message.attachments[...]
    '''
    global NEWLOCATION
    global CONTEXTS
    global USER_LANGUAGE

    # Get input data
    chat_id = user_id

    if USER_LANGUAGE == None:
        USER_LANGUAGE = get_language(user_id)

    # Get, save photos, add paths to NEWLOCATION['photos]
    if 'media_input' in CONTEXTS:
        # https://scontent.xx.fbcdn.net/v/t1.15752-9/34416397_446356285788138_8430653788502622208_n.jpg?_nc_cat=0&_nc_ad=z-m&_nc_cid=0&oh=c7c985bab096d0646ea5333064ff6651&oe=5B7F0DD6
        file_name_wo_extension = 'fellowtravelerclub-{}'.format(OURTRAVELLER)
        img_url_part1 = img_url.split('?_nc_cat')[0]
        file_extension = img_url_part1.split('.')[-1]
        current_datetime = datetime.now().strftime("%d%m%y%H%M%S")
        random_int = random.randint(100, 999)
        path4db = file_name_wo_extension + '-' + current_datetime + str(random_int) + file_extension
        path = PHOTO_DIR + path4db

        r = requests.get(img_url, timeout=0.5)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
        NEWLOCATION['photos'].append(path4db)
        users_input = 'User posted a photo'

        # Contexts - indicate that last input was an image
        if 'last_input_media' not in CONTEXTS:
            CONTEXTS.append('last_input_media')
            users_input = 'User uploaded an image'
            main_handler(users_input, chat_id, from_user, is_btn_click=False, geodata=None, media=True,
                         other_input=False)
    else:
        if 'last_input_media' not in CONTEXTS:
            CONTEXTS.append('last_input_media')
            users_input = 'Nice image ;)'
            print('Really true!')
            print('CONTEXTS: {}'.format(CONTEXTS))
            main_handler(users_input, chat_id, from_user, is_btn_click=False, geodata=None, media=True, other_input=False)


def other_content_types_handler(user_id, from_user):
    '''
        Handling other content types (audio, file, stickers (as images but with field 'sticker_id')
    '''
    global CONTEXTS
    global NEWLOCATION
    global USER_LANGUAGE
    # A fix intended not to respond to every image uploaded (if several)
    #respond_to_several_photos_only_once()

    # Get input data
    users_input = ';)'  # User entered something different from text, button_click, photo or location
    chat_id = user_id

    if USER_LANGUAGE == None:
        USER_LANGUAGE = get_language(user_id)

    # And pass it to the main handler function [main_hadler()]
    main_handler(users_input, chat_id, from_user, is_btn_click=False, geodata=None, media=False,
                 other_input=True)


def dialogflow(query, user_id, lang_code='en'):
    '''
        Function to communicate with Dialogflow for NLU
    '''
    URL = 'https://api.dialogflow.com/v1/query?v=20170712'
    print('USER_LANGUAGE: ' + lang_code)
    HEADERS = {'Authorization': 'Bearer ' + DF_TOKEN, 'content-type': 'application/json'}
    payload = {'query': query, 'sessionId': user_id, 'lang': lang_code}
    r = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    print('#####')
    print('Request from DF: ')
    print(r)
    print('#####')
    intent = r.get('result').get('metadata').get('intentName')
    speech = r.get('result').get('fulfillment').get('speech')
    status = r.get('status').get('code')
    output = {
        'status': status,
        'intent': intent,
        'speech': speech
    }
    return output

############################################ Functions END #######################################


@app.route("/")
def index():
    return "<h1 style='color:blue'>FB Messenger Bot for fellowtraveler.club</h1>"


@app.route("/webhook/", methods=['GET', 'POST'])
def message_webhook():

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
                        if message.get('message') or message.get('postback'):
                            # Get user ID
                            user_id = message.get('sender').get('id')

                            # Get user first name
                            user_first_name = get_user_firt_name(user_id)
                            from_user = ''
                            if user_first_name:
                                from_user = user_first_name

                            # Text messages (emoji also get here - may filter out later)
                            if message.get('message'):
                                if message.get('message').get('text') and not message.get('message').get('is_echo'):
                                    user_wrote = message.get('message').get('text').encode('unicode_escape')
                                    text_handler(user_id, from_user, user_wrote)
                                    #send_message(user_id, {'text': 'You said "{}'.format(user_wrote.decode('unicode_escape'))})

                                # Attachments
                                if message.get('message').get('attachments'):
                                    for attachment in message.get('message').get('attachments'):

                                        # Images (photos from camera, gifs, likes also get here)
                                        if attachment.get('type') == 'image' and not attachment.get('payload').get(
                                                'sticker_id'):
                                            img_url = attachment.get('payload').get('url')
                                            send_message(user_id, {
                                                'text': 'Img url "{}'.format(img_url)})
                                            photo_handler(user_id, from_user, img_url)

                                        # Location
                                        elif attachment.get('type') == 'location':
                                            latitude = attachment.get('payload').get('coordinates').get('lat')
                                            longitude = attachment.get('payload').get('coordinates').get('long')
                                            location_handler(user_id, from_user, latitude, longitude)

                                        # Other content types - audio, file, stickers (as images but with field 'sticker_id')
                                        else:
                                            print('Other content types')
                                            other_content_types_handler(user_id, from_user)

                            # Button clicks; persistent menu and 'Getting started' button send fixed postback in English,
                            # other buttons send postback = title in corresponding language, which is then passed to
                            # Dialogflow for NLU (thus the same commands as for these buttons can be triggered with usual text)
                            if message.get('postback') and message.get('postback').get('payload'):
                                button_payload = message.get('postback').get('payload')
                                # Two main cases:
                                # 1. Persistent menu buttons and 'Getting started' button
                                if button_payload == 'GETTING_STARTED' or button_payload == 'START_TRIGGER':
                                    getting_started(user_id)

                                elif button_payload == 'FAQ':
                                    help(user_id)

                                elif button_payload == 'CHANGE_LANGUAGE':
                                    change_language(user_id)

                                elif button_payload == 'YOU_GOT_FELLOW_TRAVELER':
                                    you_got_fellowtraveler(user_id)

                                # 2. All other buttons
                                else:
                                    button_payload = message.get('postback').get('payload')
                                    button_click_handler(user_id, from_user, button_payload)

        return "Success", 200

if __name__ == "__main__":
    print('\nFB Messenger Bot - new session\n')
    app.run(host='0.0.0.0', port=5000)
