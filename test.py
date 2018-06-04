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
