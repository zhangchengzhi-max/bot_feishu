#!/usr/bin/env python3.8

import os
import sys
import logging
import requests
import json
import asyncio
import time
import threading
import logging
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
    user_id = sender_id.user_id
    text_content = message.content
    message_api_client.send_text_with_open_id(open_id, text_content, user_id)

@event_manager.register("p2p_chat_create")
def message_first():
    print("首次会话被创建")
    return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    """
    处理错误的请求并返回相应的错误信息
    参数：
    ex -- 异常对象
    返回：
    response -- 包含错误信息的响应对象
    """
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


Info = []
def process_event():
    event_handler = Info[0]
    event = Info[1]
    event_handler(event)

@app.route("/", methods=["POST"])
def callback_event_handler():
    req = request.get_json()
    print(req)
    try:
        if 'event' in req:
            type = req['event']['message']['chat_type']
            logging.info(req['event'])
            if type == "p2p":
                global Info
                event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
                Info = [event_handler, event]

                # 开多线程处理业务逻辑
                t1 = threading.Thread(target=process_event)
                t1.start()

                print(req)
                return req
            else:
                sys.exit()
        else:
            event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
            Info = [event_handler, event]

            # 开多线程处理业务逻辑
            t1 = threading.Thread(target=process_event)
            t1.start()
            return req
    except:
        return req






if __name__ == "__main__":

    app.run(host="0.0.0.0", port=3000, debug=True)


