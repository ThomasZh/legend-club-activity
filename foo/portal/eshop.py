#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 planc2c.com
# thomas@time2box.com
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
import time
import sys
import os
import uuid
import smtplib
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
from bson import json_util
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from comm import *
from global_const import *

from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import bonus_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import vendor_member_dao
from dao import voucher_dao
from dao import insurance_template_dao
from dao import contact_dao
from dao import vendor_hha_dao
from dao import voucher_pay_dao
from dao import vendor_wx_dao
from dao import voucher_order_dao
from dao import trip_router_dao
from dao import triprouter_share_dao
from dao import club_dao
from dao import activity_share_dao


class EshopHomeHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info(self.request)

        self.redirect("/webapp/eshop/clubs/"+CLUB_ID)


class EshopIndexHandler(tornado.web.RequestHandler):
    def get(self, club_id):
        logging.info(self.request)
        logging.info("got club_id %r--------", club_id)
        vendor_id = club_id

        # club
        url = API_DOMAIN + "/api/clubs/" + club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got club response %r", response.body)
        rs = json_decode(response.body)
        club = rs['rs']

        _now = time.time()
        # 查询结果，不包含隐藏的活动
        _array = activity_dao.activity_dao().query_not_hidden_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_RECRUIT, _now, PAGE_SIZE_LIMIT)
        if len(_array) > 0 :
            for _activity in _array:
                # 金额转换成元
                if not _activity['base_fee_template']:
                    _activity['amount'] = 0
                else:
                    for base_fee_template in _activity['base_fee_template']:
                        _activity['amount'] = float(base_fee_template['fee']) / 100
                        break
        logging.info("got activity>>>>>>>>> %r", _array)

        self.render('eshop/index.html',
                API_DOMAIN=API_DOMAIN,
                club=club,
                activitys=_array)


class EshopArticleHandler(tornado.web.RequestHandler):
    def get(self, club_id, article_id):
        logging.info(self.request)
        logging.info("got article_id %r in uri", article_id)

        # club
        url = API_DOMAIN + "/api/clubs/"+club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        rs = json_decode(response.body)
        club = rs['rs']

        # update read_num
        url = API_DOMAIN + "/api/articles/"+article_id+"/read"
        http_client = HTTPClient()
        _body = {"read_num": 1}
        _json = json_encode(_body)
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got update read_num response %r", response.body)

        self.render('eshop/article.html',
                API_DOMAIN=API_DOMAIN,
                club=club,
                article_id=article_id)


class EshopProductHandler(tornado.web.RequestHandler):
    def get(self, club_id, product_id):
        logging.info(self.request)

        # club
        url = API_DOMAIN + "/api/clubs/"+club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        rs = json_decode(response.body)
        club = rs['rs']

        _activity = activity_dao.activity_dao().query(product_id)
        # 金额转换成元 默认将第一个基本服务的费用显示为活动价格
        # _activity['amount'] = float(_activity['amount']) / 100
        if not _activity['base_fee_template']:
            _activity['amount'] = 0
        else:
            for base_fee_template in _activity['base_fee_template']:
                base_fee_template['fee'] = float(base_fee_template['fee']) / 100
                _activity['amount'] = float(base_fee_template['fee']) / 100
        logging.info("got _activity response %r", _activity)

        article_id = _activity['article_id']
        # update read_num
        url = API_DOMAIN + "/api/articles/"+article_id+"/read"
        http_client = HTTPClient()
        _body = {"read_num": 1}
        _json = json_encode(_body)
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got update read_num response %r", response.body)

        self.render('eshop/product.html',
                API_DOMAIN=API_DOMAIN,
                club=club,
                article_id=article_id,
                activity=_activity)


class EshopArticleAddCommentHandler(tornado.web.RequestHandler):
    def get(self, club_id, article_id):
        logging.info(self.request)
        logging.info("got article_id %r in uri", article_id)

        # club
        url = API_DOMAIN + "/api/clubs/"+club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        rs = json_decode(response.body)
        club = rs['rs']

        self.render('eshop/add-comment.html',
                API_DOMAIN=API_DOMAIN,
                club=club,
                article_id=article_id)


class EshopProductPlaceOrderHandler(tornado.web.RequestHandler):
    def get(self, club_id, product_id):
        logging.info(self.request)
        logging.info("got product_id %r in uri", product_id)

        # club
        url = API_DOMAIN + "/api/clubs/"+club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        rs = json_decode(response.body)
        club = rs['rs']

        _activity = activity_dao.activity_dao().query(product_id)
        # 金额转换成元 默认将第一个基本服务的费用显示为活动价格
        # _activity['amount'] = float(_activity['amount']) / 100
        if not _activity['base_fee_template']:
            _activity['amount'] = 0
        else:
            for base_fee_template in _activity['base_fee_template']:
                base_fee_template['fee'] = float(base_fee_template['fee']) / 100
                _activity['amount'] = float(base_fee_template['fee']) / 100
        logging.info("got _activity response %r", _activity)

        self.render('eshop/place-order.html',
                API_DOMAIN=API_DOMAIN,
                club=club,
                activity=_activity)

    def post(self, club_id, product_id):
        logging.info(self.request)
        logging.info("got product_id %r in uri", product_id)
        vendor_id = club_id
        activity_id = product_id

        #基本服务
        base_fee_id = self.get_argument("base_fees", "")
        logging.info("got base_fee_id %r", base_fee_id)
        date = self.get_argument("date", "")
        logging.info("got date %r from argument", date)
        phone = self.get_argument("phone", "")
        logging.info("got phone %r from argument", phone)
        note = self.get_argument("note", "")
        logging.info("got note %r from argument", note)

        # 活动金额，即已选的基本服务项金额
        activity_amount = 0
        total_amount = 0
        timestamp = time.time()
        base_fees = []

        activity = activity_dao.activity_dao().query(activity_id)
        title = activity['title']
        base_fee_template = activity['base_fee_template']
        for template in base_fee_template:
            if base_fee_id == template['_id']:
                base_fee = {"_id":base_fee_id, "name":template['name'], "fee":template['fee']}
                base_fees.append(base_fee)
                activity_amount = template['fee']
                total_amount = template['fee']
                break;

        order_id = str(uuid.uuid1()).replace('-', '')
        _status = ORDER_STATUS_BF_INIT
        if total_amount == 0:
            _status = ORDER_STATUS_WECHAT_PAY_SUCCESS

        # 创建订单索引
        order_index = {
            "_id": order_id,
            "club_id": vendor_id,
            "item_type": "cake",
            "item_id": activity_id,
            "item_name": title,
            "distributor_type": "personal",
            "distributor_id": DEFAULT_USER_ID,
            "create_time": timestamp,
            "pay_type": "wxpay",
            "pay_status": _status,
            "total_amount": total_amount, #已经转换为分，注意转为数值
        }
        url = API_DOMAIN + "/api/orders"
        http_client = HTTPClient()
        _json = json_encode(order_index)
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got response.body %r", response.body)

        # status: 10=order but not pay it, 20=order and pay it.
        # pay_type: wxpay, alipay, paypal, applepay, huaweipay, ...
        order = {
            "_id": order_id,
            "guest_club_id": GUEST_CLUB_ID,
            "activity_id": activity_id,
            "account_id": DEFAULT_USER_ID,
            "account_avatar": DEFAULT_USER_AVATAR,
            "account_nickname": DEFAULT_USER_NICKNAME,
            "activity_title": title,
            "create_time": timestamp,
            "last_update_time": timestamp,
            "review": False,
            "status": _status,
            "pay_type": "wxpay",
            "total_amount": total_amount, #已经转换为分，注意转为数值
            "applicant_num": 1,
            "base_fees": base_fees, #数组
            "ext_fees": [], #数组
            "insurances": [], #数组
            "vouchers": [], #数组
            "bonus": 0, ##分，注意转为数值
            "vendor_id":vendor_id
        }
        logging.info("create order=[%r]", order)
        order_dao.order_dao().create(order)
        num = order_dao.order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "order":num})
        # TODO notify this message to vendor's administrator by SMS

        item = {}
        item["_id"] = str(uuid.uuid1()).replace('-', '')
        item["activity_id"] = activity_id
        item["order_id"] = order_id
        item["name"] = DEFAULT_USER_NICKNAME
        item["phone"] = phone
        item["note"] = note
        item["booking_time"] = date
        item["gender"] = 'male'
        item["height"] = '180'
        item["id_code"] = DEFAULT_USER_ID
        item["account_id"] = DEFAULT_USER_ID
        item["account_avatar"] = DEFAULT_USER_AVATAR
        item["account_nickname"] = DEFAULT_USER_NICKNAME
        item["create_time"] = time.time()
        item["last_update_time"] = time.time()
        item["review"] = False
        item["vendor_id"] = vendor_id
        item["activity_title"] = activity['title']
        # 取活动基本服务费用信息
        item["base_fees"] = order['base_fees']
        apply_dao.apply_dao().create(item)

        # club
        url = API_DOMAIN + "/api/clubs/"+club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        rs = json_decode(response.body)
        club = rs['rs']

        self.render('eshop/place-order-success.html',
                API_DOMAIN=API_DOMAIN,
                club=club,
                activity=activity)


class EshopProductPlaceOrderSuccessHandler(tornado.web.RequestHandler):
    def get(self, club_id, product_id):
        logging.info(self.request)
        logging.info("got product_id %r in uri", product_id)

        # club
        url = API_DOMAIN + "/api/clubs/"+club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        rs = json_decode(response.body)
        club = rs['rs']

        _activity = activity_dao.activity_dao().query(product_id)
        # 金额转换成元 默认将第一个基本服务的费用显示为活动价格
        # _activity['amount'] = float(_activity['amount']) / 100
        if not _activity['base_fee_template']:
            _activity['amount'] = 0
        else:
            for base_fee_template in _activity['base_fee_template']:
                base_fee_template['fee'] = float(base_fee_template['fee']) / 100
                _activity['amount'] = float(base_fee_template['fee']) / 100
        logging.info("got _activity response %r", _activity)

        self.render('eshop/place-order-success.html',
                API_DOMAIN=API_DOMAIN,
                club=club,
                activity=_activity)
