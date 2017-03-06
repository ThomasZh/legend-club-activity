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
from dao import bonus_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import vendor_member_dao

from global_const import VENDOR_ID
from global_const import ACTIVITY_STATUS_DRAFT
from global_const import ACTIVITY_STATUS_POP
from global_const import ACTIVITY_STATUS_DOING
from global_const import ACTIVITY_STATUS_RECRUIT
from global_const import ACTIVITY_STATUS_COMPLETED
from global_const import ACTIVITY_STATUS_CANCELED
from global_const import STP
from global_const import PAGE_SIZE_LIMIT


# 受欢迎活动列表
class ApiActivityPopularListXHR(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        #sBefore = self.get_argument("before", "") #格式 2016-06-01 22:36
        #sLimit = self.get_argument("limit", "")
        #_array = activity_dao.activity_dao().query_by_popular(vendor_id, sBefore, sLimit)
        _array = activity_dao.activity_dao().query_by_popular(vendor_id)
        for _activity in _array:
            _activity['begin_time'] = timestamp_friendly_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
            _activity['end_time'] = timestamp_friendly_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w

        docs_list = list(_array)
        self.write(JSON.dumps(docs_list, default=json_util.default))
        self.finish()

# 完成活动列表
class ApiActivityCompletedListXHR(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        before = float(self.get_argument("before", ""))
        # limit = int(self.get_argument("limit", ""))
        _array = activity_dao.activity_dao().query_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_COMPLETED, before, PAGE_SIZE_LIMIT)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)

        for _activity in _array:
            _activity['begin_time'] = timestamp_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
            _activity['end_time'] = timestamp_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w
            for category in categorys:
                if category['_id'] == _activity['category']:
                    _activity['category'] = category['title']
                    break
        docs_list = list(_array)
        self.write(JSON.dumps(docs_list, default=json_util.default))
        self.finish()
        
# 获取参加某活动的成员
class ApiActivityMemberListXHR(tornado.web.RequestHandler):
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        _array = apply_dao.apply_dao().query_by_activity(activity_id)
        for data in _array:
            _member = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, data['account_id'])
            try:
                logging.info("got account_avatar %r", _member['account_avatar'])
                data['account_avatar'] = _member['account_avatar']
            except:
                logging.warn("got account_avatar is null")

        docs_list = list(_array)
        logging.info("got json %r", JSON.dumps(docs_list, default=json_util.default))
        self.write(JSON.dumps(docs_list, default=json_util.default))
        self.finish()


# 获取参加某活动的成员
class ApiActivityInfoXHR(tornado.web.RequestHandler):
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        activity = activity_dao.activity_dao().query(activity_id)

        # 金额转换成元
        # activity['amount'] = float(activity['amount']) / 100
        for base_fee_template in activity['base_fee_template']:
            base_fee_template['fee'] = float(base_fee_template['fee']) / 100
        for ext_fee_template in activity['ext_fee_template']:
            ext_fee_template['fee'] = float(ext_fee_template['fee']) / 100

        self.write(JSON.dumps(activity, default=json_util.default))
        self.finish()


# 分享活动获得积分
class ApiActivityShareXHR(tornado.web.RequestHandler):
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        _account_id = self.get_argument("account_id", "")
        logging.info("got _account_id %r", _account_id)

        _bonus = bonus_dao.bonus_dao().query_not_safe_by_res(activity_id, _account_id, 1)
        if not _bonus:
            _bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
            _timestamp = time.time()
            _json = {'vendor_id':vendor_id, 'account_id':_account_id, 'res_id':activity_id,
                    'create_time':_timestamp, 'bonus':int(_bonus_template['activity_shared']), 'type':1}
            bonus_dao.bonus_dao().create(_json)

            _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _account_id)
            try:
                _customer_profile['comment']
            except:
                _customer_profile['comment'] = ''
            try:
                _customer_profile['bonus']
            except:
                _customer_profile['bonus'] = 0
            logging.info("got bonus %r", _customer_profile['bonus'])
            try:
                _customer_profile['history_bonus']
            except:
                _customer_profile['history_bonus'] = 0
            logging.info("got history_bonus %r", _customer_profile['history_bonus'])
            try:
                _customer_profile['distance']
            except:
                _customer_profile['distance'] = 0
            try:
                _customer_profile['rank']
            except:
                _customer_profile['rank'] = 0

            _bonus_num = int(_customer_profile['bonus']) + int(_bonus_template['activity_shared'])
            _history_bonus = int(_customer_profile['history_bonus']) + int(_bonus_template['activity_shared'])
            _json = {'vendor_id':vendor_id, 'account_id':_account_id, 'last_update_time':_timestamp,
                    'bonus':_bonus_num, 'history_bonus':_history_bonus}
            vendor_member_dao.vendor_member_dao().update(_json)
        else:
            logging.info("got _bonus['bonus'] %r", _bonus['bonus'])

        _json = {'rs':'success'}
        logging.info("got result code>>>>>>>>>>>>>>>>>>> %r", _json)
        self.write(_json)
        self.finish()
