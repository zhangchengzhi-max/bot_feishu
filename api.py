#! /usr/bin/env python3.8
import os
import sys
import logging
import requests
import time
import req_reset
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# const
TENANT_ACCESS_TOKEN_URI = "/open-apis/auth/v3/tenant_access_token/internal"
MESSAGE_URI = "/open-apis/im/v1/messages"

token_time_update = []

class MessageApiClient(object):
    def __init__(self, app_id, app_secret, lark_host):
        self._app_id = app_id
        self._app_secret = app_secret
        self._lark_host = lark_host
        self._tenant_access_token = ""

    @property
    def tenant_access_token(self):
        return self._tenant_access_token

    def send_text_with_open_id(self, open_id, content, user_id):
        self.send("open_id", open_id, "text", content, user_id)

    def send(self, receive_id_type, receive_id, msg_type, content, user_id):
        # 基于飞书api，给用户发送消息. doc link: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        self._authorize_tenant_access_token()
        url = "{}{}?receive_id_type={}".format(
            self._lark_host, MESSAGE_URI, receive_id_type
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        req_body = {
            "receive_id": receive_id,
            "content": content,
            "msg_type": msg_type,
        }

        # 获取到用户所在部门信息
        user_department, user_name = req_reset.get_department(headers, user_id)

        # 飞书根据收到的消息，来更新req_body内容，其中包括权限验证是否是EE架构的人
        # user_name = "zhangchengzhi01"
        # user_department = "EE架构-整车测试"
        req_body_update = req_reset.req_body_reset(content, user_name, user_department, receive_id, msg_type, req_body)
        # if req_body_update == req_body:
        #     sys.exit()
        # req_body['receive_id'] = 'ou_e29cf723dfa1880960c66ee555eb9165'

        requests.Session().post(url=url, headers=headers, json=req_body_update, verify=False)
        # MessageApiClient._check_error_response(resp)

    #获取token，如果判断出和上次获取token的时间差小于一小时，则不重新获取token，依旧使用原来的token
    def _authorize_tenant_access_token(self):
        global token_time_update
        try:
            if time.time() - token_time_update[1] < 3600:
                self._tenant_access_token = token_time_update[0]
                print("小于一小时", time.time() - token_time_update[1])
            else:

                url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
                req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
                response = requests.Session().post(url, req_body)
                print("大于一小时", time.time() - token_time_update[1])
                token_time_update = [response.json().get("tenant_access_token"), time.time()]
                self._tenant_access_token = response.json().get("tenant_access_token")

        except:
            print("错误，重新获取机器人token")
            url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
            req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
            response = requests.Session().post(url, req_body)
            token_time_update = [response.json().get("tenant_access_token"), time.time()]
            self._tenant_access_token = response.json().get("tenant_access_token")

        # get tenant_access_token and set, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal
        # url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
        # req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
        # # response = requests.Session().post(url, req_body)
        # # print(response.text)
        # # print(response)
        # # response = requests.post(url, req_body)
        # # MessageApiClient._check_error_response(response)
        # self._tenant_access_token = str
        # self._tenant_access_token = response.json().get("tenant_access_token")

    @staticmethod
    def _check_error_response(resp):
        # check if the response contains error information
        if resp.status_code != 200:
            resp.raise_for_status()
        response_dict = resp.json()
        code = response_dict.get("code", -1)
        if code != 0:
            logging.error(response_dict)
            raise LarkException(code=code, msg=response_dict.get("msg"))


class LarkException(Exception):
    def __init__(self, code=0, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return "{}:{}".format(self.code, self.msg)

    __repr__ = __str__
