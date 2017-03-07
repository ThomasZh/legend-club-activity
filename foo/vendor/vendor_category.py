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
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))
from comm import AuthorizationHandler
from dao import budge_num_dao
from dao import category_dao
from global_const import VENDOR_ID
import uuid

# 这里vendorid是应该动态得到并赋值
class VendorIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        self.set_secure_cookie("vendor_id", VENDOR_ID)
        self.redirect('/vendors/' + VENDOR_ID + '/categorys')


# /vendors/<string:vendor_id>/categorys/<string:category_id>/delete
class VendorCategoryDeleteHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, category_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got category_id %r in uri", category_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        category_dao.category_dao().delete(category_id)

        self.redirect('/vendors/' + vendor_id + '/categorys')


# /vendors/<string:vendor_id>/categorys
class VendorCategoryListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_myinfo_basic()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/category-list.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                categorys=categorys)


# /vendors/<string:vendor_id>/categorys/create
class VendorCategoryCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/category-create.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        title = self.get_argument("title", "")
        desc = self.get_argument("desc", "")
        bk_img_url = self.get_argument("bk_img_url", "")
        logging.debug("got param title %r", title)
        logging.debug("got param desc %r", desc)
        logging.debug("got param bk_img_url %r", bk_img_url)

        _id = str(uuid.uuid1()).replace('-', '')
        logging.info("create categroy _id %r", _id)
        categroy = {"_id":_id, "vendor_id":vendor_id,
                "title":title, "desc":desc ,"bk_img_url":bk_img_url}
        category_dao.category_dao().create(categroy);

        self.redirect('/vendors/' + vendor_id + '/categorys')


# /vendors/<string:vendor_id>/categorys/<string:category_id>/edit
class VendorCategoryEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, category_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got category_id %r in uri", category_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        category = category_dao.category_dao().query(category_id)
        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/category-edit.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                category=category)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, category_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got category_id %r in uri", category_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        title = self.get_argument("title", "")
        desc = self.get_argument("desc", "")
        bk_img_url = self.get_argument("bk_img_url", "")
        logging.debug("got param title %r", title)
        logging.debug("got param desc %r", desc)
        logging.debug("got param bk_img_url %r", bk_img_url)

        categroy = {"_id":category_id, "title":title, "desc":desc ,"bk_img_url":bk_img_url}
        category_dao.category_dao().update(categroy);

        self.redirect('/vendors/' + vendor_id + '/categorys')
