import difflib
import json
import time
import requests
import logging
from db import dbUtil
# 设置日志
logging.basicConfig(level=logging.INFO,
                    filename='log/checkLog.log',
                    filemode='a',
                    format='%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s')
user_email = ''
update_token_time = []


def get_department(headers, user_id):

    # 获取token
    url_get_token = 'https://coa-api.lixiangoa.com/oauth/token'
    req_body_token = {
        "grant_type": "client_credentials",
        "client_id": "176",
        "client_secret": "coqot2hJvSIo9MOINm4sDYUGBcpTHFVTPA6e33go",
        "scope": "*"
    }
    # 判断当前时间和上次获取token的时间差是否小于一天，若小于一天，则复用之前的token，若大于一天，则重新获取token，并更新获取token的时间
    global update_token_time
    try:
        if time.time() - update_token_time[1] < 86400:
            res_token = update_token_time[0]
            print("token时间小于一天，没过期", time.time() - update_token_time[1])
        else:
            print("token时间大于，过期了", time.time() - update_token_time[1])

            res_token = \
                requests.Session().post(url=url_get_token, json=req_body_token, verify=False, stream=True).json()[
                    'access_token']
            update_token_time = [res_token, time.time()]

    except:
        print("错误，重新获取usertoken")
        res_token = \
            requests.Session().post(url=url_get_token, json=req_body_token, verify=False, stream=True).json()[
                'access_token']
        update_token_time = [res_token, time.time()]

    # 通过token以及user_id获取到部门信息
    url_get_department = 'https://coa-api.lixiangoa.com/api/info/search_in_all_user'
    headers_get_department = {
        'Authorization': res_token
    }
    params = {
        "search_type": "feishu_user_id",
        "search_text": user_id
    }
    response = requests.Session().get(url=url_get_department, headers=headers_get_department, verify=False,
                                      params=params, stream=True).json()
    # response = http.request(method="GET", url=url_get_department, headers=headers_get_department, json=params).json()
    res_department = ''
    res_name = ''
    if len(response['data']) != 0:
        res_name = response['data'][0]['name']
        res_department = response['data'][0]['department_name_path']
    print(res_department)
    return res_department, res_name


'''
动态卡片内容
'''
def card_dynamic_content(receive_id, list_content):
    content = list_content[0]
    button_name = list_content[1]
    button_value = list_content[2]
    card_template = {
        {
  "elements": [
    {
      "tag": "markdown",
      "content": content,
      "text_align": "left"
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {
            "tag": "plain_text",
            "content": "獬豸平台网址"
          },
          "type": "primary",
          "multi_url": {
            "url": "https://vfsc-vt-qm-web.prod.k8s.lixiang.com/useCaseLibrary",
            "pc_url": "",
            "android_url": "",
            "ios_url": ""
          }
        }
      ]
    },
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "如有问题，请点击右侧的帮助按钮👉"
      },
      "extra": {
        "tag": "button",
        "text": {
          "tag": "lark_md",
          "content": "帮助"
        },
        "type": "primary",
        "value": {
          "content_card": "帮助"
        }
      }
    }
  ],
  "header": {
    "template": "blue",
    "title": {
      "content": "獬豸",
      "tag": "plain_text"
    }
  }
}
    }

def card_dynamic(receive_id, button_list):

    button1 = button_list[0]
    button2 = button_list[1]
    button3 = button_list[2]
    content_card1 = button_list[0]
    content_card2 = button_list[1]
    content_card3 = button_list[2]

    card_template = {
        "elements": [
            # {
            #     "tag": "markdown",
            #     "content": " *这是我们的门户网站：*\n          [整车自动化测试门户](https://vt.chehejia.com/#/)"
            # },
            {
                "tag": "markdown",
                "content": "*您是否需要以下业务👇：*"
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button1
                        },
                        "type": "primary",
                        "value": {
                            "content_card": content_card1
                        }
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button2
                        },
                        "type": "primary",
                        "value": {
                            "content_card": content_card2
                        }
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button3
                        },
                        "type": "primary",
                        "value": {
                            "content_card": content_card3
                        }
                    }
                ]
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "不是想要的？请点击右侧的帮助按钮获取👉"
                },
                "extra": {
                    "tag": "button",
                    "text": {
                        "tag": "lark_md",
                        "content": "帮助"
                    },
                    "type": "primary",
                    "value": {
                        "content_card": "帮助"
                    }
                }
            }
        ],
        "header": {
            "template": "blue",
            "title": {
                "content": "整车自动化测试机器人",
                "tag": "plain_text"
            }
        }
    }
    dic_json = json.dumps(card_template)
    req_body = {
        "receive_id": receive_id,
        # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
        "content": dic_json,
        "msg_type": "interactive"
    }
    return req_body


def req_body_reset(content, req_name, req_department, receive_id, msgtype, req_body):

    content_dict = json.loads(content)
    global user_email
    info_user = req_name + " " + user_email + " " + req_department + " " + content_dict['text']
    logging.info(info_user)
    req_body_update = req_body
    if content_dict['text'] in "，帮助":
        req_body_update = {
            "receive_id": receive_id,
            # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
            "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmaVvBxQXWU\"} }",
            "msg_type": "interactive"
        }
    if content_dict['text'] in "测试，工作台，獬豸，测试管理平台，用例管理平台，测试管理，用例管理,测试平台":
        if "EE架构" in req_department or "陈正人" in info_user or "张文博" in info_user:
            req_body_update = {
                "receive_id": receive_id,
                # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
                "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAwfCjjSJoG2\"} }",
                "msg_type": "interactive"
            }

        else:
            req_body_update = {
                "receive_id": receive_id,
                # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
                "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmozCovnn5W\"} }",
                "msg_type": "interactive"
            }
    if content_dict['text'] in "重名，基线测试看板，问题看板，质量看板，质量问题看板":
        req_body_update = {
            "receive_id": receive_id,
            "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmozCovneP5\"} }",
            # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
            "msg_type": "interactive"
        }
    if content_dict['text'] in "权限申请":
        req_body_update = {
            "receive_id": receive_id,
            "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAma1Bo8ujdO\"} }",
            # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
            "msg_type": "interactive"
        }
    if content_dict['text'] in "VET,问题管理，jira,JIRA,JIRA-VET,jira-vet,vet":
        req_body_update = {
            "receive_id": receive_id,
            "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
            # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
            "msg_type": "interactive"
        }
    if content_dict['text'] in "版本比对,版本，版本比对测试":
        print(req_department)
        if "整车测试部" in req_department:
            print("aaaaaaa")
            req_body_update = {
                "receive_id": receive_id,
                "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmcJpbKdOhK\"} }",
                # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
                "msg_type": "interactive"
            }
            print(req_body_update)
        else:
            req_body_update = {
                "receive_id": receive_id,
                "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmsORxiLNNg\"} }",
                # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
                "msg_type": "interactive"
            }
    if content_dict['text'] in "聚餐":
        req_body_update = {
            "receive_id": receive_id,
            "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAwM6WFd6uI4\"} }",
            # "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc51deGo4P\"} }",
            "msg_type": "interactive"
        }
    if req_body_update == req_body:
        keywords = ['帮助', '獬豸', '版本比对', '看板', '权限申请', 'JIRA-VET']
        # 初始化一个字典，用于存储关键词和它们与输入文字的相似度得分
        similarity_scores = {}

        # 使用difflib库中的get_close_matches函数计算关键词与输入文字的相似度得分
        for keyword in keywords:
            similarity = difflib.SequenceMatcher(None, content_dict['text'], keyword).ratio()
            similarity_scores[keyword] = similarity

        # 对相似度得分进行降序排序，选择得分最高的两个关键词
        sorted_keywords = sorted(similarity_scores, key=similarity_scores.get, reverse=True)[:3]
        req_body_update = card_dynamic(receive_id=receive_id, button_list=sorted_keywords)
        print(sorted_keywords)

    #     else:
    #         keywords = ['帮助', '獬豸测试用例平台', '版本比对', '看板', '权限申请', '问题反馈', '新人入职']
    #         # 初始化一个字典，用于存储关键词和它们与输入文字的相似度得分
    #         similarity_scores = {}
    #
    #         # 使用difflib库中的get_close_matches函数计算关键词与输入文字的相似度得分
    #         for keyword in keywords:
    #             similarity = difflib.SequenceMatcher(None, content_dict['text'], keyword).ratio()
    #             similarity_scores[keyword] = similarity
    #
    #         # 对相似度得分进行降序排序，选择得分最高的两个关键词
    #         sorted_keywords = sorted(similarity_scores, key=similarity_scores.get, reverse=True)[:3]
    #         req_body = card_dynamic(receive_id=receive_id, button_list=sorted_keywords)
    #         print(sorted_keywords)
    # else:
    #     # zhengxuan = 'https://www.feishu.cn/invitation/page/add_contact/?token=016g8a2c-077f-4f60-9971-dddcb1d3ee70'
    #     # content_dict['text'] = "此功能只限EE架构人员使用，敬请谅解" + "\n" + "如需使用，请联系" + zhengxuan
    #     # content = json.dumps(content_dict)
    #     # req_body['content'] = content
    #     keywords = ['獬豸，测试平台，用例平台', '版本比对', '看板', 'python', 'java']
    #     # 初始化一个字典，用于存储关键词和它们与输入文字的相似度得分
    #     similarity_scores = {}
    #     # 初始化一个字典，用于存储关键词和它们与输入文字的相似度得分
    #     similarity_scores = {}
    #
    #     # 使用difflib库中的get_close_matches函数计算关键词与输入文字的相似度得分
    #     for keyword in keywords:
    #         similarity = difflib.SequenceMatcher(None, content_dict['text'], keyword).ratio()
    #         similarity_scores[keyword] = similarity
    #
    #     # 对相似度得分进行降序排序，选择得分最高的两个关键词
    #     sorted_keywords = sorted(similarity_scores, key=similarity_scores.get, reverse=True)[:2]
    #     print(sorted_keywords)

    return req_body_update
