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
import hashlib
import sys
import os
import json as JSON # 启用别名，不会跟方法里的局部变量混淆

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
from dao import insurance_template_dao
from dao import vendor_wx_dao
from dao import vendor_hha_dao
from dao import task_dao
from dao import personal_task_dao
from dao import trip_router_dao
from dao import club_dao
from global_const import *

import html2text
import markdown
import re


class VendorSetupOperatorsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/operators.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num)


class VendorSetupInsuranceListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        _array = insurance_template_dao.insurance_template_dao().query_by_vendor(vendor_id)
        for _insurance in _array:
            # 价格转换成元
            _insurance['amount'] = float(_insurance['amount']) / 100

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/insurances.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                insurances=_array)


class VendorSetupInsuranceCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/insurance-create.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        _title = self.get_argument("title", "")
        _amount = self.get_argument("amount", "")
        # 价格转换成分
        _amount = float(_amount) * 100
        logging.info("got _title %r", _title)

        _uuid = str(uuid.uuid1()).replace('-', '')
        _insurance = {"_id":_uuid, "title":_title, "amount":_amount, "vendor_id":vendor_id}
        insurance_template_dao.insurance_template_dao().create(_insurance);

        self.redirect('/vendors/' + vendor_id + '/setup/insurances')


class VendorSetupInsuranceEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, insurance_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got insurance_id %r in uri", insurance_id)

        _insurance = insurance_template_dao.insurance_template_dao().query(insurance_id)
        # 价格转换成元
        _insurance['amount'] = float(_insurance['amount']) / 100

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/insurance-edit.html',
                vendor_id=vendor_id,
                budge_num=budge_num,
                insurance=_insurance)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, insurance_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got insurance_id %r in uri", insurance_id)

        ops = self.get_ops_info()

        _title = self.get_argument("title", "")
        _amount = self.get_argument("amount", "")
        # 价格转换成分
        _amount = float(_amount) * 100

        logging.info("got _title %r", _title)

        _insurance = {"_id":insurance_id, "title":_title, "amount":_amount}
        insurance_template_dao.insurance_template_dao().update(_insurance);

        self.redirect('/vendors/' + vendor_id + '/setup/insurances')


class VendorSetupInsuranceDeleteHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, insurance_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got insurance_id %r in uri", insurance_id)

        ops = self.get_ops_info()

        insurance_template_dao.insurance_template_dao().delete(insurance_id)

        self.redirect('/vendors/' + vendor_id + '/setup/insurances')


class VendorSetupWxHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        vendor_wx = vendor_wx_dao.vendor_wx_dao().query(vendor_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/setup-wx.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                vendor_wx=vendor_wx)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        wx_app_id = self.get_argument("wx_app_id", "")
        wx_app_secret = self.get_argument("wx_app_secret", "")
        wx_mch_id = self.get_argument("wx_mch_id", "")
        wx_mch_key = self.get_argument("wx_mch_key", "")
        wx_notify_domain = self.get_argument("wx_notify_domain", "")
        wx_qrcode = self.get_argument("wx_qrcode", "")

        vendor_wx = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        _json = {"_id":vendor_id,
                "wx_app_id":wx_app_id,
                "wx_app_secret":wx_app_secret,
                "wx_mch_id":wx_mch_id,
                "wx_mch_key":wx_mch_key,
                "wx_notify_domain":wx_notify_domain,
                "wx_qrcode":wx_qrcode}
        if not vendor_wx:
            vendor_wx_dao.vendor_wx_dao().create(_json)
        else:
            vendor_wx_dao.vendor_wx_dao().update(_json)

        self.redirect('/vendors/' + vendor_id + '/setup/wx')


class VendorSetupClubHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        club = club_dao.club_dao().query(vendor_id)
        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/setup-club.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                club=club)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        _name = self.get_argument("club_name", "")
        _desc = self.get_argument("club_desc", "")
        logo_img_url = self.get_argument("logo_img_url","")
        bk_img_url = self.get_argument("bk_img_url","")

        club = club_dao.club_dao().query_not_safe(vendor_id)
        _timestamp = time.time()
        json = {"_id":vendor_id,
                "last_update_time":_timestamp,
                "club_name":_name, "club_desc":_desc,
                "logo_img_url":logo_img_url,
                "bk_img_url":bk_img_url}
        if not club:
            club_dao.club_dao().create(json)
        else:
            club_dao.club_dao().update(json)

        self.redirect('/vendors/' + vendor_id + '/setup/club')


class VendorSetupHhaHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        vendor_hha = vendor_hha_dao.vendor_hha_dao().query(vendor_id)
        vendor_hha['content'] = markdown_html(vendor_hha['content'])

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/hold-harmless-agreements.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                vendor_hha=vendor_hha)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        content = self.get_argument("content", "")
        logging.info("got content %r", content)
        content = html_markdown(content)

        vendor_hha = vendor_hha_dao.vendor_hha_dao().query_not_safe(vendor_id)
        _json = {"_id":vendor_id,
                "content":content}
        logging.info("got _json", _json)
        if not vendor_hha:
            vendor_hha_dao.vendor_hha_dao().create(_json)
        else:
            vendor_hha_dao.vendor_hha_dao().update(_json)

        self.redirect('/vendors/' + vendor_id + '/setup/hha')


class VendorSetupTaskHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        tasks = task_dao.task_dao().query_by_vendor(vendor_id)

        for task in tasks:
            task['create_time'] = timestamp_datetime(task['create_time'])
            trip_router_id = task['triprouter']
            logging.info("got trip_router_id>>>>>>>>>> %r in uri", trip_router_id)
            triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)
            task['title'] = triprouter['title']
            task['bk_img_url'] = triprouter['bk_img_url']
            for category in categorys:
                if category['_id'] == task['category']:
                    task['category'] = category['title']
                    break

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/task-list.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                tasks=tasks)


class VendorSetupTaskDeleteHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, task_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got task_id %r in uri", task_id)

        ops = self.get_ops_info()

        task_dao.task_dao().delete(task_id)
        personal_task_dao.personal_task_dao().delete_by_task(task_id)

        self.redirect('/vendors/' + vendor_id + '/setup/task')


# VendorSetupTaskCreateHandler
class VendorSetupTaskCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        tasks= task_dao.task_dao().query_by_vendor(vendor_id)
        trip_routers = trip_router_dao.trip_router_dao().query_by_vendor(vendor_id)
         # 从所有线路里分离出没被选中任务的
        for task in tasks:
            task_trip_router = task['triprouter']
            for trip_router in trip_routers:
                trip_router_id = trip_router['_id']
                if(task_trip_router == trip_router_id):
                    trip_routers.remove(trip_router)
                    break

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/task-create.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                triprouters=trip_routers)

    def post(self,vendor_id):

        triprouters = self.get_argument("triprouters",[])
        _triprouter_ids = JSON.loads(triprouters)
        for trip_router_id in _triprouter_ids:
            trip_router = trip_router_dao.trip_router_dao().query(trip_router_id)
            _id = str(uuid.uuid1()).replace('-', '')
            _timestamp = time.time()
            _category = trip_router['category']
            _title = trip_router['title']
            _json = {"_id":_id,
                    "title":_title,
                    "vendor_id":vendor_id,
                    "triprouter":trip_router_id,
                    "category":_category,
                    "create_time":_timestamp}
            task_dao.task_dao().create(_json)

        self.redirect('/vendors/' + vendor_id + '/setup/task')

# VendorSetupTaskAllocateHandler 已被分配过任务该任务的应该不显示在列表中
class VendorSetupTaskAllocateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, task_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got task_id %r in uri", task_id)

        ops = self.get_ops_info()

        _task = task_dao.task_dao().query(task_id)
        _task['create_time'] = timestamp_datetime(_task['create_time'])

        _customers = vendor_member_dao.vendor_member_dao().query_pagination(vendor_id, 0, PAGE_SIZE_LIMIT)

        # 已分配过该任务的用户剔除
        new_customers =[]

        for _customer in _customers:
            _account_id = _customer['account_id']
            _personal_task = personal_task_dao.personal_task_dao().query_by_task_account(task_id,_account_id)
            if not _personal_task:
                new_customers.append(_customer)

        _customers = new_customers

        for _customer in _customers:
            _customer['create_time'] = timestamp_datetime(_customer['create_time'])
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

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/task-allocate.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                task=_task, customers=_customers)

    def post(self, vendor_id, task_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", task_id)

        ops = self.get_ops_info()

        _account_id = self.get_argument("account_id", "")
        logging.info("got _account_id %r", _account_id)

        _id = str(uuid.uuid1()).replace('-', '')
        _timestamp = time.time()
        json = {"_id":_id,
                "vendor_id":vendor_id,
                "create_time":_timestamp,
                "task_id":task_id,
                "account_id":_account_id,
                "status":0} # 未完成；status=1, 完成 #被分配的任务后，如果参加过某次相关活动，就应该更新这个状态

        personal_task_dao.personal_task_dao().create(json)
        self.redirect('/vendors/' + vendor_id + '/setup/task')
