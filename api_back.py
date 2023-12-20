#! /usr/bin/env python3.8
import os
import json
import logging
import requests
import time

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# const
TENANT_ACCESS_TOKEN_URI = "/open-apis/auth/v3/tenant_access_token/internal"
MESSAGE_URI = "/open-apis/im/v1/messages"


class MessageApiClient(object):
    def __init__(self, app_id, app_secret, lark_host):
        self._app_id = app_id
        self._app_secret = app_secret
        self._lark_host = lark_host
        self._tenant_access_token = ""

    @property
    def tenant_access_token(self):
        return self._tenant_access_token

    def send_text_with_open_id(self, open_id, content):
        self.send("open_id", open_id, "text", content)

    def send(self, receive_id_type, receive_id, msg_type, content):
        # send message to user, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
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

        # -------------------权限校验开始，获取到部门信息--------------------------
        '''
            首先校验是否是EE架构的人
            1.先通过open_id获取用户基本信息，得到email
            2.调用接口获取有效token，用来执行第三步
            3.通过email,token调用接口获取到部门信息
        '''
        start1 = time.time()
        # 1.得到email,字段为enterprise_email，现在用其他字段先测着点
        url_get_email = 'https://open.feishu.cn/open-apis/contact/v3/users/' + receive_id + '?department_id_type=open_department_id&user_id_type=open_id'  # receive_id就是open_id
        res = requests.Session().get(url=url_get_email, headers=headers, verify=False)
        # res = requests.get(url=url_get_email, headers=headers)
        print("调用飞书接口耗时：", time.time() - start1)
        user_email = res.json()['data']['user']['name']

        # 写死来进行正确的验证
        user_email = 'zhangchengzhi1@lixiang.com'
        # user_email = res.json()['data']['user']['enterprise_email']

        start2 = time.time()

        # 2.获取token
        url_get_token = 'https://coa-api.lixiangoa.com/oauth/token'
        req_body_token = {
            "grant_type": "client_credentials",
            "client_id": "176",
            "client_secret": "coqot2hJvSIo9MOINm4sDYUGBcpTHFVTPA6e33go",
            "scope": "*"
        }
        start_token = time.time()
        res_token = requests.Session().post(url=url_get_token, json=req_body_token, verify=False, stream=True,
                                            ).json()['access_token']
        print("获取token时间:", time.time() - start_token)
        # 3.通过token以及email获取到部门信息
        url_get_department = 'https://coa-api.lixiangoa.com/api/info/search_in_all_user'
        headers_get_department = {
            'Authorization': res_token
        }
        params = {
            "search_type": "email",
            "search_text": user_email
        }
        start3 = time.time()
        response = requests.Session().get(url=url_get_department, headers=headers_get_department, verify=False,
                                          params=params, stream=True).json()

        print("只请求：", time.time() - start3)
        res_department = ''
        if len(response['data']) != 0:
            res_department = response['data'][0]['department_name_path']
        end2 = time.time()
        print("获取token及调用获取部门信息的接口耗时：", end2 - start2)
        # 👆------------获取部门信息完成------------------👆

        # 捕获请求的内容，根据内容进行逻辑处理
        content_dict = json.loads(content)  # 得到'content':'{"text":"/text/"}', key:value,value是json格式
        res_department = ''
        if "EE架构" in res_department:
            # 捕获请求的内容，根据内容进行逻辑处理
            if content_dict['text'] in "獬豸，xiezhi":
                req_body = {
                    "receive_id": receive_id,
                    "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAqPfI0dRirg\"} }",
                    # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmcJpbKdOhK\"} }",
                    "msg_type": "interactive"
                }
            elif content_dict['text'] in "权限申请":
                req_body = {
                    "receive_id": receive_id,
                    "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAqkFeabzDnU\"} }",
                    # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
                    "msg_type": "interactive"
                }
            elif content_dict['text'] in "基线测试看板，问题看板":
                req_body = {
                    "receive_id": receive_id,
                    "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmwSW3qsg6D\"} }",
                    # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
                    "msg_type": "interactive"
                }

            elif content_dict['text'] in "新人入职指南":
                req_body = {
                    "receive_id": receive_id,
                    # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
                    "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc5sXrV7TL\"} }",
                    "msg_type": "interactive"
                }
            elif content_dict['text'] in "帮助":
                req_body = {
                    "receive_id": receive_id,
                    # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
                    "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmjOk4aQOCO\"} }",
                    "msg_type": "interactive"
                }
            elif content_dict['text'] in "问题反馈":
                req_body = {
                    "receive_id": receive_id,
                    # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
                    "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAqkFeabzDnU\"} }",
                    "msg_type": "interactive"
                }
            else:
                req_body = {
                    "receive_id": receive_id,
                    # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
                    "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmawKzWiuhu\"} }",
                    "msg_type": "interactive"
                }
        else:
            zhengxuan = 'https://www.feishu.cn/invitation/page/add_contact/?token=016g8a2c-077f-4f60-9971-dddcb1d3ee70'
            content_dict['text'] = "此功能只限EE架构人员使用，敬请谅解" + "\n" + "如需使用，请联系" + zhengxuan
            content = json.dumps(content_dict)
            req_body['content'] = content

        requests.post(url=url, headers=headers, json=req_body)


        # MessageApiClient._check_error_response(resp)

    def _authorize_tenant_access_token(self):
        # get tenant_access_token and set, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal
        url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
        req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
        response = requests.post(url, req_body)
        # MessageApiClient._check_error_response(response)
        self._tenant_access_token = response.json().get("tenant_access_token")

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