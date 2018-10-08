# -*- encoding: utf-8 -*-
from chatbot import ChatbotSimulator


cb = ChatbotSimulator(0, "Hello!", 0, 0, "fHx8")
response = cb.chatbot_response()
print response['message']



while True:
    u_msg = raw_input('\n')
    while not (u_msg):
        u_msg = raw_input('Please, enter a message...\n')
    cb = ChatbotSimulator(response['section'], u_msg, response['input'], response['retry'], response['record'])
    response = cb.chatbot_response()
    print response['message']

    while (response['retry'] == 1 or not response['message']):
        cb = ChatbotSimulator(response['section'], 'null', response['input'], response['retry'], response['record'])
        response = cb.chatbot_response()
        print response['message']



