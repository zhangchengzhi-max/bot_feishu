#!/usr/bin/env python3.8
import os
import sys
import json
import abc
import hashlib
import typing as t
import check_event_id
from utils import dict_2_obj
from flask import request, jsonify
from decrypt import AESCipher


class Event(object):
    callback_handler = None

    # event base
    def __init__(self, dict_data, token, encrypt_key):
        # event check and init
        header = dict_data.get("header")
        event = dict_data.get("event")
        if header is None or event is None:
            raise InvalidEventException("request is not callback event(v2)")
        self.header = dict_2_obj(header)
        self.event = dict_2_obj(event)
        self._validate(token, encrypt_key)

    def _validate(self, token, encrypt_key):
        if self.header.token != token:
            raise InvalidEventException("invalid token")
        timestamp = request.headers.get("X-Lark-Request-Timestamp")
        nonce = request.headers.get("X-Lark-Request-Nonce")
        signature = request.headers.get("X-Lark-Signature")
        body = request.data
        bytes_b1 = (timestamp + nonce + encrypt_key).encode("utf-8")
        bytes_b = bytes_b1 + body
        h = hashlib.sha256(bytes_b)
        # if signature != h.hexdigest():
        #     raise InvalidEventException("invalid signature in event")

    @abc.abstractmethod
    def event_type(self):
        return self.header.event_type


class MessageReceiveEvent(Event):
    # message receive event defined in https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/events/receive

    @staticmethod
    def event_type():
        return "im.message.receive_v1"


class UrlVerificationEvent(Event):

    # special event: url verification event
    def __init__(self, dict_data):
        self.event = dict_2_obj(dict_data)

    @staticmethod
    def event_type():
        return "url_verification"


class EventManager(object):
    event_callback_map = dict()
    event_type_map = dict()
    _event_list = [MessageReceiveEvent, UrlVerificationEvent]

    def __init__(self):
        for event in EventManager._event_list:
            EventManager.event_type_map[event.event_type()] = event

    def register(self, event_type: str) -> t.Callable:
        def decorator(f: t.Callable) -> t.Callable:
            self.register_handler_with_event_type(event_type=event_type, handler=f)
            return f

        return decorator

    @staticmethod
    def register_handler_with_event_type(event_type, handler):
        EventManager.event_callback_map[event_type] = handler

    @staticmethod
    def get_handler_with_event(token, encrypt_key):
        dict_data = json.loads(request.data)
        print(dict_data['header']['event_id'])
        # 检查一下是否有重复的event_id，如果有，直接退出程序（服务器还是一直开启的状态，只是后续的代码不执行了）
        result = check_event_id.check(event_id=dict_data['header']['event_id'])
        if result == False:
            # return False
            sys.exit()
        #如果没有重复的event_id,则将其保存到txt文件里，方便下次检查
        f2 = open('event_id.txt', 'a+')
        f2.write(dict_data['header']['event_id'] + "\n")
        #普通消息
        if 'encrypt' in dict_data.keys():
            dict_data = EventManager._decrypt_data(encrypt_key, dict_data)
            # print(dict_data['header']['event_id'])
            #检查一下是否有重复的event_id，如果有，直接退出程序（服务器还是一直开启的状态，只是后续的代码不执行了）
            # result = check_event_id.check(event_id=dict_data['header']['event_id'])
            # if result == False:
            #     # return False
            #     sys.exit(1)
            # #如果没有重复的event_id,则将其保存到txt文件里，方便下次检查
            # f2 = open('event_id.txt', 'a+')
            # f2.write(dict_data['header']['event_id'] + "\n")
            callback_type = dict_data.get("type")
            # only verification data has callback_type, else is event
            if callback_type == "url_verification":

                event = UrlVerificationEvent(dict_data)
                return EventManager.event_callback_map.get(event.event_type()), event

        #点击卡片回复卡片，拼接Key,value
        if 'action' in dict_data.keys():
            dict_data['schema'] = '2.0'

            event_type = {'event_type':'im.message.receive_v1'}
            dict_data['header'] = event_type
            dict_data['header']['token'] = os.getenv("VERIFICATION_TOKEN")

            sender_id = {
                'open_id': dict_data['open_id'],
                # 'union_id': 'on_6f0cfc36907161d77a3668c02573d07f',
                'user_id': dict_data['user_id']
            }
            sender = {
                'sender_id':sender_id,
                'sender_type':'user',
                'tenant_key': dict_data['tenant_key']
            }
            message = {
                'message_type': 'text',
                'content':'{"text":'+ '"'+ dict_data['action']['value']['content_card']+ '"}'
            }
            # dict_data['event'] = {'message': {'content': {"text": dict_data['action']['value']['content']}}}
            dict_data['event'] = {
                'message':message
            }
            dict_data['event']['sender'] = sender
            dict_data['event']['message']['message_type'] = 'text'
            # {'message': {'content': '{"text":"新人"}'}
        # only handle event v2

        schema = dict_data.get("schema")

        if schema is None:
            raise InvalidEventException("request is not callback event(v2)")
        # get event_type
        event_type = dict_data.get("header").get("event_type")
        # build event
        event = EventManager.event_type_map.get(event_type)(dict_data, token, encrypt_key)
        # get handler
        return EventManager.event_callback_map.get(event_type), event

    @staticmethod
    def _decrypt_data(encrypt_key, data):
        encrypt_data = data.get("encrypt")
        if encrypt_key == "" and encrypt_data is None:
            # data haven't been encrypted
            return data
        if encrypt_key == "":
            raise Exception("ENCRYPT_KEY is necessary")
        cipher = AESCipher(encrypt_key)

        return json.loads(cipher.decrypt_string(encrypt_data))

class InvalidEventException(Exception):
    def __init__(self, error_info):
        self.error_info = error_info

    def __str__(self) -> str:
        return "Invalid event: {}".format(self.error_info)

    __repr__ = __str__