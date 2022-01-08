import datetime
import telegram_send

"""
this script is used only for sending log messages to the console and to my phone (via telegram) when needed
"""

def send_log_message(message='', alert=False):
    if alert:
        telegram_send.send(messages=['[' + datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message])
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message)