#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 planc2c.com
# dev@tripc2c.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import tornado.web
import logging
import uuid
import time
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat
from bson import json_util

from comm import BaseHandler
from comm import timestamp_datetime
from comm import datetime_timestamp
from comm import timestamp_date
from comm import date_timestamp
from comm import timestamp_friendly_date

from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao


from global_const import *


# 查询blog中文章中的段落
class ApiBlogParagraphListXHR(tornado.web.RequestHandler):
    def get(self, vendor_id, article_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got article_id %r in uri", article_id)

        url = "http://"+STP+"/blogs/my-articles/" + article_id + "/paragraphs"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")

        self.write(response.body)
        self.finish()

# 查看别人分享的活动招募内容
class ApiDemoActivityParagraphXHR(tornado.web.RequestHandler):
    def get(self, vendor_id, article_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got article_id %r in uri", article_id)

        url = "http://"+STP+"/blogs/my-articles/" + article_id + "/paragraphs"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        url = API_DOMAIN +"/api/articles/" + article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        article = data['rs']
        _paragraphs = article['paragraphs']
        self.write(_paragraphs)
        self.finish()
