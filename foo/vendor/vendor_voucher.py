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
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat

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
from dao import vendor_member_dao
from dao import voucher_dao
from dao import voucher_order_dao
from dao import voucher_pay_dao
from dao import vendor_wx_dao
from global_const import *


class VendorVoucherListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        _status = self.get_argument("status", "")
        logging.info("got _status %r", _status)
        _status = int(_status)
        _before = time.time()

        #TODO 这里若有偿代金券过多会 显示过多
        if(_status == 0):
            pay_vouchers = voucher_pay_dao.voucher_pay_dao().query_pagination_by_status(vendor_id,_status,_before,PAGE_SIZE_LIMIT)
            free_vouchers = voucher_dao.voucher_dao().query_pagination_by_status(vendor_id, _status, _before, PAGE_SIZE_LIMIT)
            _vouchers = pay_vouchers + free_vouchers
        else:
            _vouchers = voucher_dao.voucher_dao().query_pagination_by_status(vendor_id, _status, _before, PAGE_SIZE_LIMIT)

        for _data in _vouchers:
            # 转换成元
            _data['amount'] = float(_data['amount']) / 100

            if _data['price'] != 0:
                _data['price'] = float(_data['price']) / 100

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

        counter = self.get_counter(vendor_id)
        self.render('vendor/vouchers.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                status=_status,
                vouchers=_vouchers)


class VendorVoucherFreeCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/vouchers-free-create.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        _amount = self.get_argument("amount", "")
        logging.info("got _amount %r", _amount)
        _expired_time = self.get_argument("expired_time", "")
        logging.info("got _expired_time %r", _expired_time)

        # 转换为分（整数）
        _amount = float(_amount) * 100
        # 转换为秒
        _expired_time = date_timestamp(_expired_time)

        _id = str(uuid.uuid1()).replace('-', '')
        _timestamp = time.time()
        json = {"_id":_id, "vendor_id":vendor_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "amount":_amount, "expired_time":_expired_time, "price":0,
                'status':0} # status=0, 未分配
        voucher_dao.voucher_dao().create(json);

        self.redirect('/vendors/' + vendor_id + '/vouchers?status=0')


# 有偿商品代金券创建
class VendorVoucherPayCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/vouchers-pay-create.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        _amount = self.get_argument("amount", "")
        logging.info("got _amount %r", _amount)
        _price = self.get_argument("price", "")
        logging.info("got price %r", _amount)
        _expired_time = self.get_argument("expired_time", "")
        logging.info("got _expired_time %r", _expired_time)

        # 转换为分（整数）
        _amount = float(_amount) * 100
        _price = float(_price) *100
        # 转换为秒
        _expired_time = date_timestamp(_expired_time)

        voucher_id = str(uuid.uuid1()).replace('-', '')

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_notify_domain = wx_app_info['wx_notify_domain']

        voucher_url = wx_notify_domain + "/bf/wx/vendors/" + vendor_id + "/vouchers/" + voucher_id
        data = {"url": voucher_url}
        _json = json_encode(data)
        logging.info("got ——json %r", _json)
        http_client = HTTPClient()
        response = http_client.fetch(QRCODE_CREATE_URL, method="POST", body=_json)
        logging.info("got response %r", response.body)
        qrcode_url = response.body
        logging.info("got qrcode_url %r", qrcode_url)

        _timestamp = time.time()
        json = {"_id":voucher_id, "vendor_id":vendor_id, "qrcode_url":qrcode_url,
                "create_time":_timestamp, "last_update_time":_timestamp, "price":_price,
                "amount":_amount, "expired_time":_expired_time, "status":0}
        voucher_pay_dao.voucher_pay_dao().create(json);

        self.redirect('/vendors/' + vendor_id + '/vouchers?status=0')


class VendorVoucherFreeEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        ops = self.get_ops_info()

        _voucher = voucher_dao.voucher_dao().query_not_safe(voucher_id)
        # 转换成元
        _voucher['amount'] = float(_voucher['amount']) / 100
        _voucher['expired_time'] = timestamp_date(_voucher['expired_time'])

        counter = self.get_counter(vendor_id)
        self.render('vendor/vouchers-free-edit.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                voucher=_voucher)

    def post(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        ops = self.get_ops_info()

        _amount = self.get_argument("amount", "")
        logging.info("got _amount %r", _amount)
        _expired_time = self.get_argument("expired_time", "")
        logging.info("got _expired_time %r", _expired_time)

        # 转换为分（整数）
        _amount = float(_amount) * 100
        # 转换为秒
        _expired_time = date_timestamp(_expired_time)

        _timestamp = time.time()
        json = {"_id":voucher_id,
                "last_update_time":_timestamp,
                "amount":_amount, "expired_time":_expired_time}
        voucher_dao.voucher_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/vouchers?status=0')


class VendorVoucherFreeAllocateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        ops = self.get_ops_info()

        _voucher = voucher_dao.voucher_dao().query_not_safe(voucher_id)
        # 转换成元
        _voucher['amount'] = float(_voucher['amount']) / 100
        _voucher['expired_time'] = timestamp_date(_voucher['expired_time'])

        _customers = vendor_member_dao.vendor_member_dao().query_pagination(vendor_id, 0, PAGE_SIZE_LIMIT)
        for _customer in _customers:
            _customer['create_time'] = timestamp_datetime(_customer['create_time']);
            try:
                _customer['account_nickname']
            except:
                _customer['account_nickname'] = ''
            try:
                _customer['account_avatar']
            except:
                _customer['account_avatar'] = ''
            try:
                _customer['rank'] = int(_customer['rank'])
            except:
                _customer['rank'] = 0
            try:
                _customer['comment']
            except:
                _customer['comment'] = ''

        counter = self.get_counter(vendor_id)
        self.render('vendor/vouchers-allocate.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                voucher=_voucher, customers=_customers)

    def post(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        ops = self.get_ops_info()

        _account_id = self.get_argument("account_id", "")
        logging.info("got _account_id %r", _account_id)

        _timestamp = time.time()
        json = {"_id":voucher_id,
                "last_update_time":_timestamp,
                "account_id":_account_id, "status":1} # status=1, 已分配
        voucher_dao.voucher_dao().update(json);

        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _account_id)
        try:
            _customer_profile['vouchers']
        except:
            _customer_profile['vouchers'] = 0
        _voucher = voucher_dao.voucher_dao().query_not_safe(voucher_id)
        _vouchers_num = int(_customer_profile['vouchers']) + int(_voucher['amount'])
        _json = {'vendor_id':vendor_id, 'account_id':_account_id, 'last_update_time':_timestamp,
                'vouchers':_vouchers_num}
        vendor_member_dao.vendor_member_dao().update(_json)

        self.redirect('/vendors/' + vendor_id + '/vouchers?status=0')


class VendorVoucherPayEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        ops = self.get_ops_info()

        _voucher = voucher_pay_dao.voucher_pay_dao().query_not_safe(voucher_id)
        # 转换成元
        _voucher['amount'] = float(_voucher['amount']) / 100
        _voucher['price'] = float(_voucher['price']) / 100
        _voucher['expired_time'] = timestamp_date(_voucher['expired_time'])

        counter = self.get_counter(vendor_id)
        self.render('vendor/vouchers-pay-edit.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                voucher=_voucher)

    def post(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        ops = self.get_ops_info()

        _amount = self.get_argument("amount", "")
        logging.info("got _amount %r", _amount)
        _price = self.get_argument("price", "")
        logging.info("got _price %r", _price)
        _expired_time = self.get_argument("expired_time", "")
        logging.info("got _expired_time %r", _expired_time)

        # 转换为分（整数）
        _amount = float(_amount) * 100
        _price = float(_price) * 100
        # 转换为秒
        _expired_time = date_timestamp(_expired_time)

        _timestamp = time.time()
        json = {"_id":voucher_id,
                "last_update_time":_timestamp,
                "amount":_amount, "price":_price,
                "expired_time":_expired_time}
        voucher_pay_dao.voucher_pay_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/vouchers?status=0')

# 有偿代金券分配即生成代金券订单，目前可无限次
class VendorVoucherPayAllocateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        ops = self.get_ops_info()

        _voucher = voucher_pay_dao.voucher_pay_dao().query_not_safe(voucher_id)
        # 转换成元
        _amount = _voucher['amount']
        _price = _voucher['price']
        _voucher_id = _voucher['_id']
        _id = str(uuid.uuid1()).replace('-', '')
        _create_time = _voucher['create_time']
        _expired_time = _voucher['expired_time']
        _qrcode_url = _voucher['qrcode_url']

        # account_id应由微信端传入
        account_id = 'feece1648fa6484086700a83b0e8e540';
        _customer = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id,account_id);
        try:
            _customer['account_nickname']
        except:
            _customer['account_nickname'] = ''
        try:
            _customer['account_avatar']
        except:
            _customer['account_avatar'] = ''

        _nickname = _customer['account_nickname']
        _avatar = _customer['account_avatar']

        # 创建一个代金券订单
        _timestamp = time.time()
        json = {"_id":_id, "vendor_id":vendor_id,
                "account_id":account_id, "account_avatar":_avatar, "account_nickname":_nickname,
                "voucher_id":_voucher_id, "voucher_price":_price, "voucher_amount":_amount,
                "pay_type":"wxpay","applicant_num":1,
                "create_time":_timestamp, "last_update_time":_timestamp,
                'status':1, 'review':False}
        voucher_order_dao.voucher_order_dao().create(json);

        # 每分配一个有偿代金券则生成一个普通代金券记录,方便个人中心查询
        _timestamp = time.time()
        json = {"_id":_id, "vendor_id":vendor_id, "qrcode_url":_qrcode_url,
                "create_time":_create_time, "last_update_time":_timestamp,
                "amount":_amount, "expired_time":_expired_time, "price":_price,
                'status':1, "account_id":account_id} # status=1, 已分配，未使用
        voucher_dao.voucher_dao().create(json);


        # 更新用户代金券
        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, account_id)
        try:
            _customer_profile['vouchers']
        except:
            _customer_profile['vouchers'] = 0
        _vouchers_num = int(_customer_profile['vouchers']) + int(_amount)
        _json = {'vendor_id':vendor_id, 'account_id':account_id, 'last_update_time':_timestamp,
                'vouchers':_vouchers_num}
        vendor_member_dao.vendor_member_dao().update(_json)

        num = voucher_order_dao.voucher_order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "voucher_order":num})

        counter = self.get_counter(vendor_id)

        self.redirect('/vendors/' + vendor_id + '/vouchers?status=0')
