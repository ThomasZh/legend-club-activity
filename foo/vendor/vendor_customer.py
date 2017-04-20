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
from dao import contact_dao
from dao import insurance_template_dao
from dao import cret_dao
from dao import task_dao
from dao import personal_task_dao
from dao import trip_router_dao
from dao import category_dao
from global_const import *


class VendorCustomerListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id,):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_access_token()
        logging.info("got access_token %r in uri",access_token)

        ops = self.get_ops_info()

        access_token = self.get_access_token()

        counter = self.get_counter(vendor_id)
        self.render('vendor/customers.html',
                vendor_id=vendor_id,
                ops=ops,
                access_token=access_token,
                counter=counter,
                keys_value="")


class VendorCustomerSearchHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        keys_value = self.get_argument("search_keys", "")
        customers = vendor_member_dao.vendor_member_dao().query_by_keys(vendor_id,keys_value)
        for _customer_profile in customers:
            _customer_profile['create_time'] = timestamp_datetime(_customer_profile['create_time']);
            try:
                _customer_profile['account_nickname']
            except:
                _customer_profile['account_nickname'] = ''
            try:
                _customer_profile['account_avatar']
            except:
                _customer_profile['account_avatar'] = ''
            logging.info("got account_avatar %r", _customer_profile['account_avatar'])
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
                _customer_profile['vouchers']
            except:
                _customer_profile['vouchers'] = 0
            # 转换成元
            _customer_profile['vouchers'] = float(_customer_profile['vouchers']) / 100
            try:
                _customer_profile['distance']
            except:
                _customer_profile['distance'] = 0
            try:
                _customer_profile['rank']
            except:
                _customer_profile['rank'] = 0
            try:
                _customer_profile['crets']
            except:
                _customer_profile['crets'] = 0

        counter = self.get_counter(vendor_id)
        self.render('vendor/customers.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                customers=customers,
                keys_value=keys_value)


class VendorCustomerProfileHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, account_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got account_id %r in uri", account_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        url = API_DOMAIN + "/api/clubs/"+vendor_id+"/users/" + account_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        _customer_profile = data['rs']

        _contacts = contact_dao.contact_dao().query_by_account(vendor_id, account_id)

        access_token = self.get_access_token()

        params = {"filter":"account", "account_id":account_id, "page":1, "limit":20,}
        url = url_concat(API_DOMAIN + "/api/orders", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        orders = rs['data']

        for order in orders:
            # 下单时间，timestamp -> %m月%d 星期%w
            order['create_time'] = timestamp_datetime(float(order['create_time']))
            # 合计金额
            order['amount'] = float(order['amount']) / 100
            order['actual_payment'] = float(order['actual_payment']) / 100

        # 取任务
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        personal_tasks = personal_task_dao.personal_task_dao().query_by_vendor_account(vendor_id,account_id)
        logging.info("got personal_tasks============ %r in uri", len(personal_tasks))

        for personal_task in personal_tasks:
            personal_task['create_time'] = timestamp_datetime(personal_task['create_time'])

            task_id = personal_task['task_id']
            task = task_dao.task_dao().query(task_id)

            trip_router_id = task['triprouter']
            triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)

            personal_task['title'] = triprouter['title']
            personal_task['bk_img_url'] = triprouter['bk_img_url']
            for category in categorys:
                if category['_id'] == task['category']:
                    personal_task['category'] = category['title']
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/customer-profile.html',
                access_token=access_token,
                vendor_id=vendor_id,
                ops=ops,
                account_id=account_id,
                counter=counter,
                profile=_customer_profile,
                contacts=_contacts, orders=orders, tasks =personal_tasks)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, account_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got account_id %r in uri", account_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        points = self.get_argument("points", "")
        logging.info("got points %r", points)
        _history_bonus = self.get_argument("history_bonus", "")
        logging.info("got _history_bonus %r", _history_bonus)
        vouchers = self.get_argument("vouchers", "")
        logging.info("got vouchers %r", vouchers)
        mileage = self.get_argument("mileage", "")
        logging.info("got mileage %r", mileage)
        star = self.get_argument("star", "")
        logging.info("got star %r", star)

        json = {'_rank':0, 'star':star, 'points':points,'vouchers':vouchers, 'mileage':mileage}

        url = "http://7x24hs.com/api/clubs/"+vendor_id+"/users/"+account_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode(json)
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/customers/' + account_id)


# 用户的某个证书信息
class VendorCustomerCretInfoHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, cret_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got cret_id %r in uri", cret_id)

        ops = self.get_ops_info()

        _cret = cret_dao.cret_dao().query(cret_id)

        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _cret['account_id'])
        try:
            _customer_profile['account_nickname']
        except:
            _customer_profile['account_nickname'] = ''
        try:
            _customer_profile['account_avatar']
        except:
            _customer_profile['account_avatar'] = ''

        counter = self.get_counter(vendor_id)
        self.render('vendor/customer-cret-info.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                profile=_customer_profile,
                cret=_cret)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, cret_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got cret_id %r in uri", cret_id)

        ops = self.get_ops_info()

        distance = self.get_argument("distance", "")
        hours = self.get_argument("hours", "")
        height = self.get_argument("height", "")
        speed = self.get_argument("speed", "")
        road_map_url = self.get_argument("road_map_url", "")
        contour_map_url = self.get_argument("contour_map_url", "")
        logging.info("got road_map_url %r", road_map_url)
        logging.info("got contour_map_url %r", contour_map_url)

        _timestamp = time.time()
        json = {"_id":cret_id,
                "last_update_time":_timestamp,
                "distance":distance, "hours":hours, "height":height,
                "speed":speed, "road_map_url":road_map_url, "contour_map_url":contour_map_url}
        cret_dao.cret_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/crets/' + cret_id)
