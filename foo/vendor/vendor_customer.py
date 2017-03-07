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

        ops = self.get_myinfo_basic()

        customers = vendor_member_dao.vendor_member_dao().query_pagination(vendor_id, 0, PAGE_SIZE_LIMIT)
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

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/customers.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                customers=customers,
                keys_value="")



class VendorCustomerSearchHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_myinfo_basic()

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

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/customers.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                customers=customers,
                keys_value=keys_value)


class VendorCustomerProfileHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, account_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got account_id %r in uri", account_id)

        ops = self.get_myinfo_basic()

        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, account_id)
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
        logging.info("got vouchers %r", _customer_profile['vouchers'])
        try:
            _customer_profile['distance']
        except:
            _customer_profile['distance'] = 0
        try:
            _customer_profile['rank']
        except:
            _customer_profile['rank'] = 0

        _contacts = contact_dao.contact_dao().query_by_account(vendor_id, account_id)
        before = time.time()
        _orders = order_dao.order_dao().query_pagination_by_vendor_account(vendor_id, account_id, before, PAGE_SIZE_LIMIT)
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

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/customer-profile.html',
                vendor_id=vendor_id,
                ops=ops,
                account_id=account_id,
                budge_num=budge_num,
                profile=_customer_profile,
                contacts=_contacts, orders=_orders, tasks =personal_tasks)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, account_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got account_id %r in uri", account_id)

        ops = self.get_myinfo_basic()

        _comment = self.get_argument("comment", "")
        logging.info("got _comment %r", _comment)
        _bonus = self.get_argument("bonus", "")
        logging.info("got _bonus %r", _bonus)
        _history_bonus = self.get_argument("history_bonus", "")
        logging.info("got _history_bonus %r", _history_bonus)
        _vouchers = self.get_argument("vouchers", "")
        logging.info("got _vouchers %r", _vouchers)
        _vouchers = float(_vouchers) * 100 # 转换成分
        _distance = self.get_argument("distance", "")
        logging.info("got _distance %r", _distance)
        _rank = self.get_argument("rank", "")
        logging.info("got _rank %r", _rank)

        _timestamp = time.time()
        _json = {'vendor_id':VENDOR_ID, 'account_id':account_id, 'last_update_time':_timestamp,
                'bonus':_bonus, 'history_bonus':_history_bonus, 'vouchers':_vouchers,
                'rank':_rank, 'comment':_comment, 'distance':_distance}
        vendor_member_dao.vendor_member_dao().update(_json)

        self.redirect('/vendors/' + vendor_id + '/customers/' + account_id)


# 用户的某个证书信息
class VendorCustomerCretInfoHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, cret_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got cret_id %r in uri", cret_id)

        ops = self.get_myinfo_basic()

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

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/customer-cret-info.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                profile=_customer_profile,
                cret=_cret)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, cret_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got cret_id %r in uri", cret_id)

        ops = self.get_myinfo_basic()

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
