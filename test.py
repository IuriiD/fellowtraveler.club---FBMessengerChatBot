# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../ft')
import facebook
import requests
import json
import ft_functions
from keys import DF_TOKEN, GOOGLE_MAPS_API_KEY, MAIL_PWD, FB_ACCESS_TOKEN, FB_VERIFY_TOKEN
graph = facebook.GraphAPI(access_token=FB_ACCESS_TOKEN, version="2.2")

OURTRAVELLER = 'Teddy'
PHOTO_DIR = '../ft/static/uploads/{}/'.format(OURTRAVELLER) # where photos from places visited are saved
SERVICE_IMG_DIR = '../ft/static/uploads/{}/service/'.format(OURTRAVELLER) # where 'general info' images are saved (summary map, secret code example etc)


def get_user_first_name(user_id):
    '''
        Retrieves user first name using Facebook Graph API for a user with user_id
    '''
    user = graph.get_object(id=str(user_id))
    if user.get('first_name'):
        return user.get('first_name')
    else:
        return False

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

def send_text_message_share_location(user_id, text):
    '''
    Sends a text message (text) to FB user with user_id with a quick reply button for sharing location
    '''
    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                        params = {'access_token': FB_ACCESS_TOKEN},
                        data = json.dumps(
                            {
                                'recipient': {'id': user_id},
                                'message': {
                                    'text': text,
                                'quick_replies': [
                                    {
                                        'content_type': 'location'
                                    }
                                ]
                                }
                            }
                        ),
                        headers={'Content-type': 'application/json'}
                      )
    if r.status_code != requests.codes.ok:
        print(r.text)

#send_text_message_share_location('1953498254661052', 'Hello')

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

def save_static_map(traveller):
    '''
    https://developers.google.com/maps/documentation/static-maps/intro
    Requests a list of places visited by traveller from DB and draws a static (png) map
    '''
    print('\nsave_static_map()')
    try:
        markers = ft_functions.get_location_history(traveller, PHOTO_DIR)['mymarkers'][::-1]
        latlongparams = ''
        for index, marker in enumerate(markers):
            latlongparams += '&markers=color:green%7Clabel:{}%7C{},{}'.format(index + 1, marker['lat'], marker['lng'])

        query = 'https://maps.googleapis.com/maps/api/staticmap?size=700x400&maptype=roadmap{}&key={}'.format(latlongparams, GOOGLE_MAPS_API_KEY)
        print('query: {}'.format(query))

        path = PHOTO_DIR + traveller + '_summary_map.png'

        r = requests.get(query, timeout=0.5)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)

        return True
    except Exception as e:
        print('save_static_map() exception: {}'.format(e))
        return False

user_id = '1953498254661052'
print(save_static_map('Teddy'))

curl -X POST -H "Content-Type: application/json" -d '{
  "recipient":{
    "id":"<PSID>"
  },
  "sender_action":"typing_on"
}' "https://graph.facebook.com/v2.6/me/messages?access_token=<PAGE_ACCESS_TOKEN>"


'''
lat = '49.4410043'
long = '32.064902'
img = 'https://maps.googleapis.com/maps/api/staticmap?key={}&markers=color:green|{},{}&size=700x400&maptype=roadmap'.format(
            GOOGLE_MAPS_API_KEY, lat, long)

send_generic_template_message(user_id, title='TestTitle', subtitle='Somethinelse', image_url=img, buttons=[
    {
        'type': 'postback',
        'title': 'Btn1',
        'payload': 'Btn1'
    }
])

for index, marker in enumerate(markers):
    latlongparams += '&markers=color:green%7Clabel:{}%7C{},{}'.format(index + 1, marker['lat'], marker['lng'])
query = 'https://maps.googleapis.com/maps/api/staticmap?size=700x400&maptype=roadmap{}&key={}'.format(latlongparams, GOOGLE_MAPS_API_KEY)


send_text_message('1953498254661052','https://www.google.com/maps/@49.4444086,32.0469634,15z')

curl  \
  -F 'recipient={"id":"1953498254661052"}' \
  -F 'message={"attachment":{"type":"image", "payload":{"is_reusable"=true}}}' \
  -F 'filedata=@/vagrant/teddygo/ft/static/uploads/biography.jpg;type=image/jpg' \
  "https://graph.facebook.com/v2.6/me/messages?access_token=EAADGEqL1NYABADEU1ITeQWyXDAnZBg70dbHZBWvDGSFbSfqDOWIciSD99ya0Gqaa1gksxoZBBbOlQ4J229EEbddFGHZCHlJbhZBe61p3Q3yZCaz5D5Ipr7VWY7pbS3i8OhvobT9vH4Eqa5C771C4fSYKljzSUAAljEBoc2A2lFYAZDZD"

curl -X POST -H "Content-Type: application/json" -d '{
  "message":{
    "attachment":{
      "type":"image",
      "payload":{
        "is_reusable": true,
        "url":"https://fellowtraveler.club/static/uploads/Teddy/fellowtravelerclub-Teddy-060518131443213.jpg"
      }
    }
  }
}' "https://graph.facebook.com/v2.6/me/message_attachments?access_token=EAADGEqL1NYABADEU1ITeQWyXDAnZBg70dbHZBWvDGSFbSfqDOWIciSD99ya0Gqaa1gksxoZBBbOlQ4J229EEbddFGHZCHlJbhZBe61p3Q3yZCaz5D5Ipr7VWY7pbS3i8OhvobT9vH4Eqa5C771C4fSYKljzSUAAljEBoc2A2lFYAZDZD"

"196520410973040"\

curl -X POST -H "Content-Type: application/json" -d '{
  "recipient":{
    "id":"<PSID>"
  },
  "message":{
    "attachment": {
      "type": "template",
      "payload": {
         "template_type": "media",
         "elements": [
            {
               "media_type": "<image|video>",
               "attachment_id": "<ATTACHMENT_ID>"
            }
         ]
      }
    }
  }
}' "https://graph.facebook.com/v2.6/me/messages?access_token=<PAGE_ACCESS_TOKEN>"    

// several images were uploaded
{
    'entry': [
        {
            'messaging': [
                {
                    'timestamp': 1528108716004,
                    'message': {
                        'mid': 'mid.$cAAD51gHPijRp-6XX5FjymBZcaX9s',
                        'seq': 12772,
                        'attachments': [

                            {'type': 'image',
                             'payload': {
                                 'url': 'https://scontent.xx.fbcdn.net/v/t1.15752-9/34334499_446356315788135_4093339648267386880_n.jpg?_nc_cat=0&_nc_ad=z-m&_nc_cid=0&oh=57d1ffd3b20ab0e41cd26b91c1c9c3bb&oe=5BBCE23C'
                                }
                             },

                            {
                                'type': 'image',
                                'payload': {
                                    'url': 'https://scontent.xx.fbcdn.net/v/t1.15752-9/34384020_446356255788141_7540926874772307968_n.jpg?_nc_cat=0&_nc_ad=z-m&_nc_cid=0&oh=8f6f13880b2630f113b08dee47083c9b&oe=5B76E514'
                                }
                            },

                            {
                                'type': 'image',
                                'payload': {
                                    'url': 'https://scontent.xx.fbcdn.net/v/t1.15752-9/34335432_446356262454807_4395999362187001856_n.jpg?_nc_cat=0&_nc_ad=z-m&_nc_cid=0&oh=e5b1ddec49bebb69ed6f33fcef36b032&oe=5BB9A250'
                                }
                            },

                            {
                                'type': 'image',
                                'payload': {
                                    'url': 'https://scontent.xx.fbcdn.net/v/t1.15752-9/34416397_446356285788138_8430653788502622208_n.jpg?_nc_cat=0&_nc_ad=z-m&_nc_cid=0&oh=c7c985bab096d0646ea5333064ff6651&oe=5B7F0DD6'
                                }
                            }
                        ]
                    },
                    'sender': {
                        'id': '1953498254661052'
                    },
                    'recipient': {
                        'id': '179374839354264'
                    }
                }
            ],
            'time': 1528108716272,
            'id': '179374839354264'
        }
    ],
    'object': 'page'
}




[
    {
      "locale":"default",
      "composer_input_disabled": false,
      "call_to_actions":[
          {
              "title": "Tell your story",
              "type": "postback",
              "payload": "Tell your story"
          },
          {
              "title": "FAQ/Settings",
              "type": "nested",
              "call_to_actions":[
                  {
                      "title": "FAQ",
                      "type": "postback",
                      "payload": "FAQ"
                  },
                  {
                      "title": "Change language",
                      "type": "postback",
                      "payload": "CHANGE_LANGUAGE"
                  }
              ]
          },
          {
              "title": "I've got a fellow traveler",
              "type": "postback",
              "payload": "YOU_GOT_FELLOW_TRAVELER"
          }
          ]
      },
      {
          "locale": "uk_UA",
          "composer_input_disabled": false,
          "call_to_actions": [
              {
                  "title": "Розкажи свою історію",
                  "type": "postback",
                  "payload": "Розкажи свою історію"
              },
              {
                  "title": "ЧаПи/Настройки",
                  "type": "nested",
                  "call_to_actions": [
                      {
                          "title": "ЧаПи",
                          "type": "postback",
                          "payload": "FAQ"
                      },
                      {
                          "title": "Змінити мову",
                          "type": "postback",
                          "payload": "CHANGE_LANGUAGE"
                      }
                  ]
              },
              {
                  "title": "Мені дістався попутник",
                  "type": "postback",
                  "payload": "YOU_GOT_FELLOW_TRAVELER"
              }
          ]
      },
      {
          "locale":"ru_RU",
          "composer_input_disabled": false,
          "call_to_actions": [
              {
                  "title": "Расскажи свою историю",
                  "type": "postback",
                  "payload": "Расскажи свою историю"
              },
              {
                  "title": "ЧаВо/Настройки",
                  "type": "nested",
                  "call_to_actions": [
                      {
                          "title": "ЧаВо",
                          "type": "postback",
                          "payload": "FAQ"
                      },
                      {
                          "title": "Сменить язык",
                          "type": "postback",
                          "payload": "CHANGE_LANGUAGE"
                      }
                  ]
              },
              {
                  "title": "Мне достался попутчик",
                  "type": "postback",
                  "payload": "YOU_GOT_FELLOW_TRAVELER"
              }
          ]
      }
      ]
'''