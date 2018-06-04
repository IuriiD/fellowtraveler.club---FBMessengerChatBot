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
              "title": "Start",
              "type": "postback",
              "payload": "START_TRIGGER"
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
                  "title": "Початок",
                  "type": "postback",
                  "payload": "START_TRIGGER"
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
                  "title": "Начало",
                  "type": "postback",
                  "payload": "START_TRIGGER"
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
