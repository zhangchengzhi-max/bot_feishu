#!/usr/bin/env python3.8

import os
import logging
import requests
import json
import asyncio
import time
import threading
from api import MessageApiClient
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from flask import Flask, jsonify, request
from dotenv import load_dotenv, find_dotenv

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)

# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")

# init service
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
event_manager = EventManager()


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message

    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()
        # get open_id and text_content

    open_id = sender_id.open_id
    text_content = message.content
    # echo text message
    # print(open_id, text_content, "&&&&&&&&&&&&&")
    start = time.time()
    message_api_client.send_text_with_open_id(open_id, text_content)
    print("耗时n:", time.time()-start)

    # return jsonify()

# @event_manager.register("im.message.receive_v1")
# async def message_receive_event_handler(req_data: MessageReceiveEvent):
#     sender_id = req_data.event.sender.sender_id
#     message = req_data.event.message
#
#     if message.message_type != "text":
#         logging.warn("Other types of messages have not been processed yet")
#         return jsonify()
#         # get open_id and text_content
#     async def service():
#         open_id = sender_id.open_id
#         text_content = message.content
#         # echo text message
#         # print(open_id, text_content, "&&&&&&&&&&&&&")
#         message_api_client.send_text_with_open_id(open_id, text_content)
#     asyncio.create_task(service())
#     return jsonify()

@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response







# import time
#
# async def tt():
#     time.sleep(5)
#     print("***************-")
#
# Info = {}
# def process_event():
#
#     start = time.time()
#     event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
#     end = time.time()
#     print('耗时1 --- ', end - start)
#     # event_handler(event)
#     time.sleep(1.6)
#     print('耗时2 ---', time.time()-end)
#
#
#
# def Check_status():
#     while True:
#         if Info.get('status') == 'ok':
#             # process_event()
#             tt()
#             print('事件处理完成...')
#             Info['status'] = 'suc'
#         time.sleep(2)
#         print('解析数据-无满足条件数据，跳过...')

@app.route("/", methods=["POST"])
async def callback_event_handler():
    global Info

    req = request.get_json()
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)

    # req = request.get_json()
    #
    # asyncio.create_task(tt())
    # process_event()
    Info['status'] = 'ok'

    return 'OK'

@app.route("/res", methods=["POST"])
async def callback_event_handler2():
    # start = time.time()
    # print(request.get_json())
    # try:
    #     asyncio.create_task(process_event())
    # except:
    #     pass
    # print('耗时：', time.time()-start)
    # return "success"

    req = request.get_json()
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
    event_handler(event)

    return req

    # return event_handler(event)


if __name__ == "__main__":
    # init()
    # t1 = threading.Thread(target=Check_status)
    # t1.start()
    app.run(host="0.0.0.0", port=3000, debug=True)

