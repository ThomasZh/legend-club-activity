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
import re
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

        # url = "http://"+STP+"/blogs/my-articles/" + article_id + "/paragraphs"
        # http_client = HTTPClient()
        # response = http_client.fetch(url, method="GET")
        url = API_DOMAIN + "/api/articles/" + article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        article = data['rs']
        _paragraphs = article['paragraphs']

        # 为图片延迟加载准备数据
        # < img alt="" src="http://bighorn.b0.upaiyun.com/blog/2016/11/2/758f7478-d406-4f2e-9566-306a963fb979" />
        # < img data-original="真实图片" src="占位符图片">
        ptn="(<img src=\"http[s]*://[\w\.\/\-]+\" />)"
        img_ptn = re.compile(ptn)
        imgs = img_ptn.findall(_paragraphs)
        for img in imgs:
            logging.info("got img %r", img)
            ptn="<img src=\"(http[s]*://[\w\.\/\-]+)\" />"
            url_ptn = re.compile(ptn)
            urls = url_ptn.findall(_paragraphs)
            url = urls[0]
            logging.info("got url %r", url)
            #html = html.replace(img, "< img class=\"lazy\" data-original=\""+url+"\" src=\"/static/images/weui.png\" width=\"100%\" height=\"480\" />")
            _paragraphs = _paragraphs.replace(img, "<img width='100%' src='"+url+"' />")

        logging.info("got _paragraphs>>>>>>>>>>> %r", _paragraphs)

        self.write(_paragraphs)
        self.finish()
