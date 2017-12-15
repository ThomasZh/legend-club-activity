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

from global_const import *
from comm import AuthorizationHandler
from comm import timestamp_datetime
from comm import datetime_timestamp
from comm import timestamp_date
from comm import date_timestamp

from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import insurance_template_dao
from dao import vendor_member_dao
from dao import voucher_order_dao
from dao import vendor_wx_dao


class VendorOrdersMeAllHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-all.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersMeNoneHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-none.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersMeOtherHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        club_id = self.get_argument("club_id", "")

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-other.html',
                vendor_id=vendor_id,
                club_id=club_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersMeOthersHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-others.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersOtherMeHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        club_id = self.get_argument("club_id", "")

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-other-me.html',
                vendor_id=vendor_id,
                club_id=club_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersOthersMeHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-others-me.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorApplyListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/applys.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorVoucherOrderListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_access_token()

        ops = self.get_ops_info()

        before = time.time()
        _array = voucher_order_dao.voucher_order_dao().query_pagination_by_vendor(vendor_id, before, PAGE_SIZE_LIMIT);
        for _voucher_order in _array:
            _voucher_order['voucher_price'] = float(_voucher_order['voucher_price'])/100
            _voucher_order['voucher_amount'] = float(_voucher_order['voucher_amount'])/100
            _voucher_order['create_time'] = timestamp_datetime(_voucher_order['create_time'])

        counter = self.get_counter(vendor_id)
        self.render('vendor/voucher-orders.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter,
                voucher_orders= _array)


class VendorOrderInfoHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)
        access_token = self.get_access_token()

        ops = self.get_ops_info()

        order_index = self.get_order_index(order_id)
        logging.info("got order_index %r in uri", order_index)
        order_index['create_time'] = timestamp_datetime(order_index['create_time'])
        order_index['booking_time'] = timestamp_datetime(order_index['booking_time'])
        order = self.get_symbol_object(order_id)

        for base_fee in order['base_fees']:
            # 价格转换成元
            order['activity_amount'] = float(base_fee['fee']) / 100

        for _voucher in order['vouchers']:
            # 价格转换成元
            _voucher['fee'] = float(_voucher['fee']) / 100

        for ext_fee in order['ext_fees']:
            # 价格转换成元
            ext_fee['fee'] = float(ext_fee['fee']) / 100

        for insurance in order['insurances']:
            # 价格转换成元
            insurance['fee'] = float(insurance['fee']) / 100

        order['amount'] = float(order['amount']) / 100
        order['points_used'] = float(order['points_used']) / 100
        order_index['actual_payment'] = float(order_index['actual_payment']) / 100
        order_index['amount'] = float(order_index['amount']) / 100

        params = {"filter":"order", "order_id":order_id, "page":1, "limit":20}
        url = url_concat(API_DOMAIN + "/api/applies", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        applies = rs['data']

        for _apply in applies:
            # 下单时间，timestamp -> %m月%d 星期%w
            _apply['create_time'] = timestamp_datetime(float(_apply['create_time']))
            if _apply['gender'] == 'male':
                _apply['gender'] = u'男'
            else:
                _apply['gender'] = u'女'

        counter = self.get_counter(vendor_id)
        self.render('vendor/order-detail.html',
                vendor_id=vendor_id,
                ops=ops,
                access_token=access_token,
                counter=counter,
                order_index=order_index,
                order=order,
                applies=applies)


# 结算
class VendorSupplierBalanceHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        counter = self.get_counter(vendor_id)
        self.render('vendor/supplier-balance.html',
                access_token=access_token,
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                api_domain = API_DOMAIN)


class VendorResellerBalanceHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        counter = self.get_counter(vendor_id)
        self.render('vendor/reseller-balance.html',
                access_token=access_token,
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                api_domain = API_DOMAIN)


class VendorSupplierBalanceDetailsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, account_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got account_id %r in uri", account_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        counter = self.get_counter(vendor_id)
        self.render('vendor/supplier-balance-details.html',
                access_token=access_token,
                vendor_id=vendor_id,
                account_id=account_id,
                ops=ops,
                counter=counter,
                api_domain = API_DOMAIN)


class VendorResellerBalanceDetailsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, org_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got org_id %r in uri", org_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        counter = self.get_counter(vendor_id)
        self.render('vendor/reseller-balance-details.html',
                access_token=access_token,
                vendor_id=vendor_id,
                org_id=org_id,
                ops=ops,
                counter=counter,
                api_domain = API_DOMAIN)


# 供应商发起提现申请
class VendorSupplierApplyCashoutHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, club_id, league_id):
        logging.info(self.request)
        ops = self.get_ops_info()

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(club_id)
        wx_notify_domain = wx_app_info['wx_notify_domain']

        # create wechat qrcode
        apply_cashout_wx_url = wx_notify_domain + "/bf/wx/vendors/" + club_id + "/ops/" + ops['account_id'] +"/apply-cash-out/leagues/" + league_id
        logging.info("got apply_cashout_wx_url %r", apply_cashout_wx_url)
        data = {"url": apply_cashout_wx_url}
        _json = json_encode(data)
        http_client = HTTPClient()
        response = http_client.fetch(QRCODE_CREATE_URL, method="POST", body=_json)
        logging.info("got response %r", response.body)
        qrcode_url = response.body
        logging.info("got qrcode_url %r", qrcode_url)

        counter = self.get_counter(club_id)
        self.render('vendor/apply-cash-out.html',
                ops=ops,
                counter=counter,
                vendor_id=club_id,
                qrcode_url=qrcode_url,
                api_domain=API_DOMAIN)


# 分销商发起提现申请
class VendorResellerApplyCashoutHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, club_id, supplier_id):
        logging.info(self.request)
        ops = self.get_ops_info()

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(club_id)
        wx_notify_domain = wx_app_info['wx_notify_domain']

        # create wechat qrcode
        apply_cashout_wx_url = wx_notify_domain + "/bf/wx/vendors/" + club_id + "/ops/" + ops['account_id'] +"/apply-cash-out/suppliers/" + supplier_id
        logging.info("got apply_cashout_wx_url %r", apply_cashout_wx_url)
        data = {"url": apply_cashout_wx_url}
        _json = json_encode(data)
        http_client = HTTPClient()
        response = http_client.fetch(QRCODE_CREATE_URL, method="POST", body=_json)
        logging.info("got response %r", response.body)
        qrcode_url = response.body
        logging.info("got qrcode_url %r", qrcode_url)

        counter = self.get_counter(club_id)
        self.render('vendor/apply-cash-out.html',
                ops=ops,
                counter=counter,
                vendor_id=club_id,
                qrcode_url=qrcode_url,
                api_domain=API_DOMAIN)


# 我在联盟中的积分
class VendorLeagueBalanceHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        counter = self.get_counter(vendor_id)
        self.render('vendor/league-balance.html',
                access_token=access_token,
                vendor_id=vendor_id,
                org_id=vendor_id,
                ops=ops,
                counter=counter,
                api_domain = API_DOMAIN)


# 积分提现记录
class VendorApplyCashoutLogHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, league_id):
        logging.info("got league_id %r in uri", league_id)

        ops = self.get_ops_info()
        logging.info("got ops %r", ops)
        access_token = self.get_access_token()

        counter = self.get_counter(ops['club_id'])
        self.render('vendor/apply-cashout-log.html',
                access_token=access_token,
                league_id=league_id,
                vendor_id = ops['club_id'],
                ops=ops,
                counter=counter,
                api_domain = API_DOMAIN)
