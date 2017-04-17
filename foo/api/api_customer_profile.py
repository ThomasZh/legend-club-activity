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

from comm import *

from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import voucher_dao
from dao import vendor_member_dao
from dao import contact_dao
from dao import insurance_template_dao
from dao import cret_dao


from global_const import ACTIVITY_STATUS_DRAFT
from global_const import ACTIVITY_STATUS_POP
from global_const import ACTIVITY_STATUS_DOING
from global_const import ACTIVITY_STATUS_RECRUIT
from global_const import ACTIVITY_STATUS_COMPLETED
from global_const import ACTIVITY_STATUS_CANCELED
from global_const import STP
from global_const import PAGE_SIZE_LIMIT


class ApiCustomerListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id,):
        logging.info("got vendor_id %r in uri", vendor_id)
        page = self.get_argument("page", 1)
        logging.debug("get page=[%r] from argument", page)
        limit = self.get_argument("limit", 20)
        logging.debug("get limit=[%r] from argument", limit)

        access_token = self.get_access_token()

        params = {"page":page, "limit":limit}
        url = url_concat(API_DOMAIN + "/api/clubs/"+vendor_id+"/users", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        users = rs['data']

        _json = JSON.dumps(users, default=json_util.default)
        logging.info("got _customer_profile %r", _json)
        self.write(_json)
        self.finish()


# 查询 代金券列表
class ApiCustomerProfileVoucherListXHR(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        _status = self.get_argument("status", "")
        logging.info("got _status %r", _status)
        _status = int(_status)

        iBefore = 0
        sBefore = self.get_argument("before", "") #格式 2016-06-01 22:36
        if sBefore != "":
            iBefore = float(datetime_timestamp(sBefore))
        else:
            iBefore = time.time()

        account_id = self.get_secure_cookie("account_id")
        if(account_id !=""):
            _vouchers = voucher_dao.voucher_dao().query_pagination_by_vendor(vendor_id, account_id, _status, iBefore, PAGE_SIZE_LIMIT)

            logging.info("got _account_id %r", account_id)
        else:
            _vouchers = voucher_dao.voucher_dao().query_pagination_by_status(vendor_id, _status, iBefore, PAGE_SIZE_LIMIT)

        for _data in _vouchers:
            # 转换成元
            _data['amount'] = float(_data['amount']) / 100
            _data['expired_time'] = timestamp_date(_data['expired_time'])
            _data['create_time'] = timestamp_datetime(_data['create_time'])


            if _data['status'] != 0:
                _customer = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _data['account_id'])
                try:
                    _customer['account_nickname']
                except:
                    _customer['account_nickname'] = ''
                try:
                    _customer['account_avatar']
                except:
                    _customer['account_avatar'] = ''
                _data['account_nickname'] = _customer['account_nickname']
                _data['account_avatar'] = _customer['account_avatar']

        _json = JSON.dumps(_vouchers, default=json_util.default)
        logging.info("got _vouchers %r", _json)

        self.write(_json)
        self.finish()


class ApiCustomerProfileMyInfoXHR(BaseHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        _account_id = self.get_secure_cookie("account_id")
        logging.info("got _account_id %r", _account_id)
        _customer_profile = self.get_club_user(vendor_id, _account_id)

        _json = JSON.dumps(_customer_profile, default=json_util.default)
        logging.info("got _customer_profile %r", _json)
        self.write(_json)
        self.finish()


# 获取当前用户的联系人（以前报名时添加的人）
class ApiCustomerProfileMyContactListXHR(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        account_id = self.get_secure_cookie("account_id")
        logging.info("got _account_id %r", account_id)

        contacts = contact_dao.contact_dao().query_by_account(vendor_id, account_id);
        self.write(JSON.dumps(contacts, default=json_util.default))
        self.finish()


# 获取当前用户的历史活动
class ApiCustomerProfileHistoryActivityXHR(tornado.web.RequestHandler):
    def get(self,vender_id):
        account_id = self.get_argument("account_id")
        logging.info("got _account_id %r", account_id)
        sBefore = self.get_argument("before", "")
        if sBefore != "":
          iBefore = float(datetime_timestamp(sBefore))
        else:
          iBefore = time.time()
        logging.info("got iBefore>>>> %r in uri", iBefore)
        _orders = order_dao.order_dao().query_pagination_by_account(account_id, iBefore, PAGE_SIZE_LIMIT)
        for order in _orders:
            _activity = activity_dao.activity_dao().query(order['activity_id'])
            order['activity_title'] = _activity['title']
            order['create_time'] = timestamp_datetime(order['create_time'])
            logging.info("got activity_title %r", order['activity_title'])
            order['activity_begin_time'] = timestamp_datetime(_activity['begin_time'])
            order['activity_distance'] = _activity['distance']
            order['activity_status'] = _activity['status']

            order_fees = []
            for ext_fee_id in order['ext_fees']:
                for template in _activity['ext_fee_template']:
                    if ext_fee_id == template['_id']:
                        json = {"_id":ext_fee_id, "name":template['name'], "fee":template['fee']}
                        order_fees.append(json)
                        break
            order['fees'] = order_fees

            order_insurances = []
            for insurance_id in order['insurances']:
                _insurance = insurance_template_dao.insurance_template_dao().query(insurance_id)
                order_insurances.append(_insurance)
            order['insurances'] = order_insurances

            _cret = cret_dao.cret_dao().query_by_account(order['activity_id'], order['account_id'])
            if _cret:
                logging.info("got _cret_id %r", _cret['_id'])
                order['cret_id'] = _cret['_id']
            else:
                order['cret_id'] = None

        _json = json_encode(_orders)
        self.write(_json)
        self.finish()
