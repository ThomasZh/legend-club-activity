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
import xlwt
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
from dao import cret_dao
from dao import vendor_member_dao
from dao import voucher_order_dao
from dao import club_dao

from global_const import *


class ApiOrderListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        product_type = self.get_argument("product_type", "all")
        logging.debug("get product_type=[%r] from argument", product_type)
        distributor_id = self.get_argument("distributor_id", "none")
        logging.debug("get distributor_id=[%r] from argument", distributor_id)
        page = self.get_argument("page", 1)
        logging.debug("get page=[%r] from argument", page)
        limit = self.get_argument("limit", 20)
        logging.debug("get limit=[%r] from argument", limit)

        access_token = self.get_access_token()

        params = {"club_id":vendor_id, "distributor_id":distributor_id, "page":page, "limit":limit, "product_type": product_type}
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
            order['total_amount'] = float(order['total_amount']) / 100
            order['payed_total_fee'] = float(order['payed_total_fee']) / 100

        self.write(JSON.dumps(rs, default=json_util.default))
        self.finish()


# 我的活动 别人的订单
class ApiLeagueOtherOrderListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()

        iBefore = 0
        sBefore = self.get_argument("before", "") #格式 2016-06-01 22:36
        if sBefore != "":
            iBefore = float(datetime_timestamp(sBefore))
        else:
            iBefore = time.time()

        _array = order_dao.order_dao().query_pagination_by_vendor_notme(vendor_id, iBefore, PAGE_SIZE_LIMIT);
        for order in _array:
            # 这里要处理一下俱乐部名称
            if order.has_key('guest_club_id'):
                if order['guest_club_id']:
                    guest_club_id = order["guest_club_id"]
                    club = get_club_info(access_token,guest_club_id)
                    if club:
                        order['guest_club_name'] = club['name']
                    else:
                        order['guest_club_name'] = ""
                else:
                    order['guest_club_name'] = ""
            else:
                order['guest_club_name'] = ""

            _activity = activity_dao.activity_dao().query(order['activity_id'])
            order['activity_title'] = _activity['title']

            try:
                order['base_fees']
            except:
                order['base_fees'] = _activity['base_fee_template']
                # 数据库apply无base_fees时，取order的赋值给它，并更新其数据库字段
                _json = {"_id":order['_id'],"base_fees":order['base_fees']}
                logging.info("got base_fees json %r in uri", _json)
                order_dao.order_dao().update(_json)

            order['activity_amount'] = 0
            if order['base_fees']:
                for base_fee in order['base_fees']:
                    # 价格转换成元
                    order['activity_amount'] = float(base_fee['fee']) / 100

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

            for _voucher in order['vouchers']:
                # 价格转换成元
                _voucher['fee'] = float(_voucher['fee']) / 100

            try:
                order['bonus']
            except:
                order['bonus'] = 0
            # 价格转换成元
            order['bonus'] = float(order['bonus']) / 100
            try:
                order['payed_total_fee'] = float(order['payed_total_fee']) / 100
            except:
                order['payed_total_fee'] = 0

            order['create_time'] = timestamp_datetime(order['create_time'])

        _json = json_encode(_array)
        logging.info("got _json %r", _json)

        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()


#别人活动我的订单
class ApiLeagueMyOrderListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_access_token()

        iBefore = 0
        sBefore = self.get_argument("before", "") #格式 2016-06-01 22:36
        if sBefore != "":
            iBefore = float(datetime_timestamp(sBefore))
        else:
            iBefore = time.time()

        _array = order_dao.order_dao().query_pagination_by_vendor_me(vendor_id, iBefore, PAGE_SIZE_LIMIT);

        for order in _array:
            # 取俱乐部名称
            club_id = order['vendor_id']
            club = get_club_info(access_token,club_id)
            if club:
                order['club_name'] = club['name']
            else:
                order['club_name'] = ""

            _activity = activity_dao.activity_dao().query(order['activity_id'])
            order['activity_title'] = _activity['title']

            try:
                order['base_fees']
            except:
                order['base_fees'] = _activity['base_fee_template']
                # 数据库apply无base_fees时，取order的赋值给它，并更新其数据库字段
                _json = {"_id":order['_id'],"base_fees":order['base_fees']}
                logging.info("got base_fees json %r in uri", _json)
                order_dao.order_dao().update(_json)

            order['activity_amount'] = 0
            if order['base_fees']:
                for base_fee in order['base_fees']:
                    # 价格转换成元
                    order['activity_amount'] = float(base_fee['fee']) / 100

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

            for _voucher in order['vouchers']:
                # 价格转换成元
                _voucher['fee'] = float(_voucher['fee']) / 100

            try:
                order['bonus']
            except:
                order['bonus'] = 0
            # 价格转换成元
            order['bonus'] = float(order['bonus']) / 100
            try:
                order['payed_total_fee'] = float(order['payed_total_fee']) / 100
            except:
                order['payed_total_fee'] = 0

            order['create_time'] = timestamp_datetime(order['create_time'])

        _json = json_encode(_array)
        logging.info("got _json %r", _json)

        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()


# 查询订单详情
class ApiOrderInfoXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        _order = order_dao.order_dao().query(order_id)
        # 价格转换成元
        _order['total_amount'] = float(_order['total_amount']) / 100
        try:
            _order['payed_total_fee']
        except:
            _order['payed_total_fee'] = 0
        _order['payed_total_fee'] = float(_order['payed_total_fee']) / 100
        for ext_fee in _order['ext_fees']:
            # 价格转换成元
            ext_fee['fee'] = float(ext_fee['fee']) / 100
        for insurance in _order['insurances']:
            # 价格转换成元
            insurance['fee'] = float(insurance['fee']) / 100
        # 价格转换成元
        _order['bonus'] = float(_order['bonus']) / 100

        for _voucher in _order['vouchers']:
            # 价格转换成元
            _voucher['fee'] = float(_voucher['fee']) / 100

        _json = JSON.dumps(_order, default=json_util.default)
        logging.info("got order %r", _json)

        self.write(_json)
        self.finish()


class ApiApplyListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        iBefore = 0
        sBefore = self.get_argument("before", "") #格式 2016-06-01 22:36
        if sBefore != "":
            iBefore = float(datetime_timestamp(sBefore))
        else:
            iBefore = time.time()

        _array = apply_dao.apply_dao().query_pagination_by_vendor(vendor_id, iBefore, PAGE_SIZE_LIMIT);
        for _apply in _array:
            _activity = activity_dao.activity_dao().query(_apply['activity_id'])
            _apply['activity_title'] = _activity['title']
            logging.info("got activity_title %r", _apply['activity_title'])
            _apply['create_time'] = timestamp_datetime(_apply['create_time'])

            try:
                _apply['base_fees']
            except:
                order = order_dao.order_dao().query(_apply['order_id'])
                _apply['base_fees'] = order['base_fees']
                # 数据库apply无base_fees时，取order的赋值给它，并更新其数据库字段
                _json = {"_id":_apply['_id'],"base_fees":order['base_fees']}
                logging.info("got base_fees json %r in uri", _json)
                apply_dao.apply_dao().update(_json)

            if len(_apply['base_fees']) == 0:
                order = order_dao.order_dao().query(_apply['order_id'])
                _json = {"_id":_apply['_id'],"base_fees":order['base_fees']}
                logging.info("got base_fees json %r in uri", _json)
                apply_dao.apply_dao().update(_json)

            customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _apply['account_id'])

            if(customer_profile):
                try:
                    customer_profile['account_nickname']
                except:
                    customer_profile['account_nickname'] = ''
                try:
                    customer_profile['account_avatar']
                except:
                    customer_profile['account_avatar'] = ''

                _apply['account_nickname'] = customer_profile['account_nickname']
                _apply['account_avatar'] = customer_profile['account_avatar']
            else:
                _apply['account_nickname'] = ''
                _apply['account_avatar'] = ''

            if _apply['gender'] == 'male':
                _apply['gender'] = u'男'
            else:
                _apply['gender'] = u'女'

        _json = json_encode(_array)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()


class ApiOrderReviewXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        _timestamp = time.time()
        json = {"_id":order_id, "last_update_time":_timestamp, "review":True}
        order_dao.order_dao().update(json);

        num = order_dao.order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "order":num})

        self.finish("ok")


class ApiOrderDeleteXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        order_dao.order_dao().delete(order_id);

        num = order_dao.order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "order":num})

        self.finish("ok")


class ApiApplyReviewXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, apply_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got apply_id %r in uri", apply_id)

        _timestamp = time.time()
        json = {"_id":apply_id, "last_update_time":_timestamp, "review":True}
        apply_dao.apply_dao().update(json);

        num = apply_dao.apply_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "application":num})

        self.finish("ok")


# 报名报表导出excel格式文件,
# 使用时必须先生成文件，然后再下载
class ApiActivityExportXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        # utf8,gbk,gb2312
        _unicode = 'utf8'
        _file = xlwt.Workbook(encoding=_unicode) # Workbook

        activity = activity_dao.activity_dao().query(activity_id)
        for base_fee in activity['base_fee_template']:
            _table = _file.add_sheet(base_fee['name'])        # new sheet

            # column names
            rownum = 0
            _table.write(rownum, 0, unicode(u'姓名').encode(_unicode))
            _table.write(rownum, 1, unicode(u'性别').encode(_unicode))
            _table.write(rownum, 2, unicode(u'身份证号码').encode(_unicode))
            _table.write(rownum, 3, unicode(u'电话号码').encode(_unicode))
            _table.write(rownum, 4, unicode(u'身高cm').encode(_unicode))
            _table.write(rownum, 5, unicode(u'备注').encode(_unicode))
            _table.write(rownum, 6, unicode(u'报名时间').encode(_unicode))

            # table
            rownum = 1
            _applys = apply_dao.apply_dao().query_by_activity(activity_id)
            for _apply in _applys:
                for apply_base_fee in _apply['base_fees']:
                    if apply_base_fee['name'] == base_fee['name']:

                        _apply['create_time'] = timestamp_datetime(_apply['create_time'])
                        try:
                            _apply['note']
                        except:
                            _apply['note'] = ''
                        if _apply['gender'] == 'male':
                            _apply['gender'] = unicode(u'男').encode(_unicode)
                        else:
                            _apply['gender'] = unicode(u'女').encode(_unicode)

                        _table.write(rownum, 0, _apply['name'])
                        _table.write(rownum, 1, _apply['gender'])
                        _table.write(rownum, 2, _apply['id_code'])
                        _table.write(rownum, 3, _apply['phone'])
                        _table.write(rownum, 4, _apply['height'])
                        _table.write(rownum, 5, _apply['note'])
                        _table.write(rownum, 6, _apply['create_time'])
                        rownum = rownum + 1

        _file.save('static/report/'+activity_id+'.xls')     # Save file
        self.finish(JSON.dumps("http://riding.time2box.com/static/report/"+activity_id+".xls"))


class ApiVoucherOrderReviewXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, voucher_order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_order_id %r in uri", voucher_order_id)

        _timestamp = time.time()
        json = {"_id":voucher_order_id, "last_update_time":_timestamp, "review":True}
        voucher_order_dao.voucher_order_dao().update(json);

        num = voucher_order_dao.voucher_order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "voucher_order":num})

        self.finish("ok")


class ApiVoucherOrderListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        iBefore = 0
        sBefore = self.get_argument("before", "") #格式 2016-06-01 22:36
        if sBefore != "":
            iBefore = float(datetime_timestamp(sBefore))
        else:
            iBefore = time.time()

        _array = voucher_order_dao.voucher_order_dao().query_pagination_by_vendor(vendor_id, iBefore, PAGE_SIZE_LIMIT);

        for _voucher_order in _array:
            _voucher_order['voucher_price'] = float(_voucher_order['voucher_price'])/100
            _voucher_order['voucher_amount'] = float(_voucher_order['voucher_amount'])/100
            _voucher_order['create_time'] = timestamp_datetime(_voucher_order['create_time'])

        _json = json_encode(_array)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()


class ApiApplySearchXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        _keys = self.get_argument("keysValue", "")
        _type = self.get_argument("searchType","")

        if(_type == 'title'):
            _array = apply_dao.apply_dao().query_by_title_keys(vendor_id,_keys);
        elif(_type == 'nickname'):
            _array = apply_dao.apply_dao().query_by_nickname_keys(vendor_id,_keys);
        elif(_type == 'date'):
            keys_array = _keys.split('~')
            begin_keys = float(date_timestamp(keys_array[0]))
            end_keys = float(date_timestamp(keys_array[1]))
            _array = apply_dao.apply_dao().query_by_time_keys(vendor_id,begin_keys,end_keys);
            logging.info("got begin_keys--------- %r in uri", begin_keys)
            logging.info("got end_keys--------- %r in uri", end_keys)
        else:
            _array = []

        if(_array):
            for _apply in _array:
                _activity = activity_dao.activity_dao().query(_apply['activity_id'])
                _apply['activity_title'] = _activity['title']
                logging.info("got activity_title %r", _apply['activity_title'])
                _apply['create_time'] = timestamp_datetime(_apply['create_time'])

                customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _apply['account_id'])

                if(customer_profile):
                    try:
                        customer_profile['account_nickname']
                    except:
                        customer_profile['account_nickname'] = ''
                    try:
                        customer_profile['account_avatar']
                    except:
                        customer_profile['account_avatar'] = ''

                    _apply['account_nickname'] = customer_profile['account_nickname']
                    _apply['account_avatar'] = customer_profile['account_avatar']
                else:
                    _apply['account_nickname'] = ''
                    _apply['account_avatar'] = ''

                if _apply['gender'] == 'male':
                    _apply['gender'] = u'男'
                else:
                    _apply['gender'] = u'女'

        _json = json_encode(_array)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()


class ApiOrderSearchXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        _keys = self.get_argument("keysValue", "")
        _type = self.get_argument("searchType","")

        if(_type == 'order'):
            _array = order_dao.order_dao().query_by_order_keys(vendor_id,_keys);
        elif(_type == 'title'):
            _array = apply_dao.apply_dao().query_by_title_keys(vendor_id,_keys);
        elif(_type == 'nickname'):
            _array = order_dao.order_dao().query_by_nickname_keys(vendor_id,_keys);
        elif(_type == 'date'):
            keys_array = _keys.split('~')
            begin_keys = float(date_timestamp(keys_array[0]))
            end_keys = float(date_timestamp(keys_array[1]))
            logging.info("got begin_keys>>>>>>>>>>> %r in uri", begin_keys)
            logging.info("got end_keys>>>>>>>>>>> %r in uri", end_keys)
            _array = order_dao.order_dao().query_by_time_keys(vendor_id,begin_keys,end_keys)
        else:
            _array = []

        if(_array):
            for order in _array:
                _activity = activity_dao.activity_dao().query(order['activity_id'])
                order['activity_title'] = _activity['title']
                # order['activity_amount'] = _activity['amount']
                if not order['base_fees']:
                    order['activity_amount'] = 0
                else:
                    for base_fee in order['base_fees']:
                        # 价格转换成元
                        order['activity_amount'] = float(base_fee['fee']) / 100

                logging.info("got activity_title %r", order['activity_title'])
                order['create_time'] = timestamp_datetime(order['create_time'])

                customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, order['account_id'])

                if(customer_profile):
                    try:
                        customer_profile['account_nickname']
                    except:
                        customer_profile['account_nickname'] = ''
                    try:
                        customer_profile['account_avatar']
                    except:
                        customer_profile['account_avatar'] = ''

                    order['account_nickname'] = customer_profile['account_nickname']
                    order['account_avatar'] = customer_profile['account_avatar']
                else:
                    order['account_nickname'] = ''
                    order['account_avatar'] = ''

                try:
                    order['bonus']
                except:
                    order['bonus'] = 0
                # 价格转换成元
                order['bonus'] = float(order['bonus']) / 100
                try:
                    order['prepay_id']
                except:
                    order['prepay_id'] = ''
                try:
                    order['transaction_id']
                except:
                    order['transaction_id'] = ''
                try:
                    order['payed_total_fee']
                except:
                    order['payed_total_fee'] = 0

                for ext_fee in order['ext_fees']:
                    # 价格转换成元
                    ext_fee['fee'] = float(ext_fee['fee']) / 100

                for insurance in order['insurances']:
                    # 价格转换成元
                    insurance['fee'] = float(insurance['fee']) / 100

                for _voucher in order['vouchers']:
                    # 价格转换成元
                    _voucher['fee'] = float(_voucher['fee']) / 100

                _cret = cret_dao.cret_dao().query_by_account(order['activity_id'], order['account_id'])
                if _cret:
                    logging.info("got _cret_id %r", _cret['_id'])
                    order['cret_id'] = _cret['_id']
                else:
                    order['cret_id'] = None

                # order['activity_amount'] = float(_activity['amount']) / 100
                if not order['base_fees']:
                    order['activity_amount'] = 0
                else:
                    for base_fee in order['base_fees']:
                        # 价格转换成元
                        order['activity_amount'] = float(base_fee['fee']) / 100

                order['total_amount'] = float(order['total_amount']) / 100
                order['payed_total_fee'] = float(order['payed_total_fee']) / 100

        _json = json_encode(_array)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()
