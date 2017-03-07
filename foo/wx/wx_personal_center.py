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
import re
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
import sys
import os
import math
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
from dao import voucher_dao
from dao import insurance_template_dao
from dao import contact_dao
from dao import cret_dao
from dao import task_dao
from dao import personal_task_dao
from dao import trip_router_dao
from dao import evaluation_dao

from auth import ssoLogin

from wx_wrap import getAccessTokenByClientCredential
from wx_wrap import getJsapiTicket
from wx_wrap import Sign
from wx_wrap import getNonceStr
from wx_wrap import getOrderSign
from wx_wrap import getPaySign
from wx_wrap import getAccessToken
from wx_wrap import getUserInfo
from xml_parser import parseWxOrderReturn, parseWxPayReturn

from global_const import VENDOR_ID
from global_const import ACTIVITY_STATUS_DRAFT
from global_const import ACTIVITY_STATUS_POP
from global_const import ACTIVITY_STATUS_DOING
from global_const import ACTIVITY_STATUS_RECRUIT
from global_const import ACTIVITY_STATUS_COMPLETED
from global_const import ACTIVITY_STATUS_CANCELED
from global_const import ORDER_STATUS_BF_INIT
from global_const import ORDER_STATUS_WECHAT_UNIFIED_SUCCESS
from global_const import ORDER_STATUS_WECHAT_UNIFIED_FAILED
from global_const import ORDER_STATUS_WECHAT_PAY_SUCCESS
from global_const import ORDER_STATUS_WECHAT_PAY_FAILED
from global_const import ORDER_STATUS_BF_APPLY_REFUND
from global_const import ORDER_STATUS_BF_REFUND_SUCCESS
from global_const import ORDER_STATUS_BF_APPLY
from global_const import ORDER_STATUS_BF_DELIVER
from global_const import ORDER_STATUS_BF_COMMENT
from global_const import STP
from global_const import WX_APP_ID
from global_const import WX_APP_SECRET
from global_const import WX_MCH_ID
from global_const import WX_MCH_KEY
from global_const import WX_NOTIFY_DOMAIN
from global_const import PAGE_SIZE_LIMIT


# 活动首页
class WxPcHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_secure_cookie("vendor_id", VENDOR_ID)
        self.redirect('/bf/wx/vendors/' + VENDOR_ID + '/pc')


# 个人中心首页
class WxPersonalCenterHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        tmp_session_ticket = None
        tmp_account_id = None
        tmp_account_nickname = None
        tmp_account_avatar = None
        tmp_wx_openid = None

        user_agent = self.request.headers["User-Agent"]
        lang = self.request.headers["Accept-Language"]
        wx_openid = self.get_secure_cookie("wx_openid")
        logging.info("got wx_openid=[%r] from cookie", wx_openid)

        if not wx_openid:
            wx_code = self.get_argument("code", "")
            logging.info("got wx_code=[%r] from argument", wx_code)

            if not wx_code or wx_code == '' :
                _url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + WX_APP_ID + "&redirect_uri=" + WX_NOTIFY_DOMAIN + "/bf/wx/vendors/" + vendor_id + "/pc&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect"
                logging.info("redirect to %r", _url)
                self.redirect(_url)
            else:
                accessToken = getAccessToken(WX_APP_ID, WX_APP_SECRET, wx_code);
                access_token = accessToken["access_token"];
                logging.info("got access_token %r", access_token)
                wx_openid = accessToken["openid"];
                logging.info("got wx_openid %r", wx_openid)

                wx_userInfo = getUserInfo(access_token, wx_openid)
                nickname = wx_userInfo["nickname"]
                #nickname = unicode(nickname).encode('utf-8')
                logging.info("got nickname=[%r]", nickname)
                headimgurl = wx_userInfo["headimgurl"]
                logging.info("got headimgurl=[%r]", headimgurl)
                tmp_account_nickname = nickname
                tmp_account_avatar = headimgurl

                # 表情符号乱码，无法存入数据库，所以过滤掉
                try:
                    # UCS-4
                    Emoji = re.compile(u'[\U00010000-\U0010ffff]')
                    nickname = Emoji.sub(u'\u25FD', nickname)
                    # UCS-2
                    Emoji = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                    nickname = Emoji.sub(u'\u25FD', nickname)
                    logging.info("got nickname=[%r]", nickname)
                except re.error:
                    logging.error("got nickname=[%r]", nickname)
                    nickname = "anonymous"

                # 1604=wechat
                stpSession = ssoLogin(1604, wx_openid, nickname, headimgurl, user_agent, lang)
                account_id = stpSession["accountId"]
                session_ticket = stpSession["sessionToken"]
                logging.info("got account_id=[%r] from neuron-stp", account_id)
                logging.info("got session_ticket=[%r] from neuron-stp", session_ticket)

                tmp_session_ticket = session_ticket
                tmp_account_id = account_id
                tmp_wx_openid = wx_openid

                self.set_secure_cookie("session_ticket", session_ticket)
                self.set_secure_cookie("account_id", account_id)
                self.set_secure_cookie("account_nickname", nickname)
                self.set_secure_cookie("account_avatar", headimgurl)
                self.set_secure_cookie("wx_openid", wx_openid)
        else:
            account_nickname = self.get_secure_cookie("account_nickname")
            account_avatar = self.get_secure_cookie("account_avatar")
            # 1604=wechat
            stpSession = ssoLogin(1604, wx_openid, account_nickname, account_avatar, user_agent, lang)
            account_id = stpSession["accountId"]
            session_ticket = stpSession["sessionToken"]
            logging.info("got account_id=[%r] from neuron-stp", account_id)
            logging.info("got session_ticket=[%r] from neuron-stp", session_ticket)

            tmp_session_ticket = session_ticket
            tmp_account_id = account_id
            tmp_account_nickname = account_nickname
            tmp_account_avatar = account_avatar
            tmp_wx_openid = wx_openid

            self.set_secure_cookie("account_id", account_id)
            self.set_secure_cookie("session_ticket", session_ticket)

        logging.info("got account_id %r", tmp_account_id)
        logging.info("got session_ticket %r", tmp_session_ticket)
        logging.info("got account_avatar %r", tmp_account_avatar)
        logging.info("got account_nickname %r", tmp_account_nickname)
        logging.info("got wx_openid %r", tmp_wx_openid)

        timestamp = time.time()
        vendor_member = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, tmp_account_id)
        if not vendor_member:
            memeber_id = str(uuid.uuid1()).replace('-', '')
            _json = {'_id':memeber_id, 'vendor_id':vendor_id,
                'account_id':tmp_account_id, 'account_nickname':tmp_account_nickname, 'account_avatar':tmp_account_avatar,
                'comment':'...',
                'bonus':0, 'history_bonus':0, 'vouchers':0, 'crets':0,
                'rank':0, 'tour_leader':False,
                'distance':0,
                'create_time':timestamp, 'last_update_time':timestamp}
            vendor_member_dao.vendor_member_dao().create(_json)
            logging.info("create vendor member %r", account_id)
        else:
            _json = {'vendor_id':vendor_id,
                'account_id':tmp_account_id, 'account_nickname':tmp_account_nickname, 'account_avatar':tmp_account_avatar,
                'last_update_time':timestamp}
            vendor_member_dao.vendor_member_dao().update(_json)

        customer_profile = vendor_member_dao.vendor_member_dao().query(vendor_id, tmp_account_id)
        # 转换成元
        try:
            customer_profile['vouchers']
        except:
            customer_profile['vouchers'] = 0
        customer_profile['vouchers'] = float(customer_profile['vouchers']) / 100

        # 加上任务数量
        personal_tasks = personal_task_dao.personal_task_dao().query_by_vendor_account(vendor_id,account_id)
        customer_profile['tasks'] = len(personal_tasks)

        self.render('wx/personal-center.html',
                vendor_id=vendor_id,
                profile=customer_profile)


# 我的历史订单列表页 @2016/06/07
# 微信用户授权成功后回调用
class WxPcOrderListHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        _tab = self.get_argument("tab", "")
        logging.info("got _tab %r", _tab)

        #_account_id = "728cce49388f423c9c464c4a97cc0a1a"
        account_id = self.get_secure_cookie("account_id")
        logging.info("got account_id=[%r] from cookie", account_id)

        before = time.time()
        orders = order_dao.order_dao().query_pagination_by_account(account_id, before, PAGE_SIZE_LIMIT)
        for order in orders:
            activity = activity_dao.activity_dao().query(order['activity_id'])
            order['activity_title'] = activity['title']
            logging.info("got activity_title %r", order['activity_title'])
            order['activity_bk_img_url'] = activity['bk_img_url']
            order['create_time'] = timestamp_datetime(order['create_time'])
            # 价格转换成元
            order['total_amount'] = float(order['total_amount']) / 100
            for base_fee in order['base_fees']:
                # 价格转换成元
                order['activity_amount'] = float(base_fee['fee']) / 100

        self.render('wx/my-orders.html',
                vendor_id=vendor_id,
                orders=orders,
                tab=int(_tab))


# 我的代金券列表页
class WxPcVoucherListHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        _account_id = self.get_secure_cookie("account_id")
        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _account_id)
        if not _customer_profile:
            _customer_profile = {'vouchers':0}
        else:
            try:
                _customer_profile['vouchers']
            except:
                _customer_profile['vouchers'] = 0


        # 有效的代金券
        _before = time.time()
        _status = 1 # 未使用
        new_voucher_amount = 0 #新的有效代金券总数
        _vouchers = voucher_dao.voucher_dao().query_pagination_by_vendor(vendor_id, _account_id, _status, _before, PAGE_SIZE_LIMIT)
        for _data in _vouchers:
            new_voucher_amount = new_voucher_amount + _data['amount']
            # 转换成元
            _data['amount'] = float(_data['amount']) / 100
            _data['expired_time'] = timestamp_friendly_date(_data['expired_time'])

        # 修改个人代金券信息
        if new_voucher_amount < 0:
            new_voucher_amount = 0
        _timestamp = time.time();
        _json = {'vendor_id':vendor_id, 'account_id':_account_id, 'last_update_time':_timestamp,
                'vouchers':new_voucher_amount}
        vendor_member_dao.vendor_member_dao().update(_json)
        _customer_profile['vouchers'] = new_voucher_amount

        # 转换成元
        _customer_profile['vouchers'] = float(_customer_profile['vouchers']) / 100

        self.render('wx/my-vouchers.html',
                vendor_id=vendor_id,
                vouchers_num=_customer_profile['vouchers'],
                vouchers=_vouchers)


# 我的微信订单详情页 @2016/06/08
class WxPcOrderInfoHandler(tornado.web.RequestHandler):
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        order = order_dao.order_dao().query(order_id)
        _activity = activity_dao.activity_dao().query(order['activity_id'])
        # FIXME, 将服务模板转为字符串，客户端要用
        _servTmpls = _activity['ext_fee_template']
        _activity['json_serv_tmpls'] = tornado.escape.json_encode(_servTmpls);
        # 按报名状况查询每个活动的当前状态：
        # 0: 报名中, 1: 已成行, 2: 已满员, 3: 已结束
        # @2016/06/06
        #
        # 当前时间大于活动结束时间 end_time， 已结束
        # 否则
        # member_max: 最大成行人数, member_min: 最小成行人数
        # 小于member_min, 报名中
        # 大于member_min，小于member_max，已成行
        # 大于等于member_max，已满员
        _now = time.time();
        _member_min = int(_activity['member_min'])
        _member_max = int(_activity['member_max'])
        if _now > _activity['end_time']:
            _activity['phase'] = '3'
        else:
            _applicant_num = apply_dao.apply_dao().count_by_activity(_activity['_id'])
            _activity['phase'] = '2' if _applicant_num >= _member_max else '1'
            _activity['phase'] = '0' if _applicant_num < _member_min else '1'
        # FIXME, 日期的格式化处理放在活动状态划分之后，不然修改了结束时间后就没法判断状态了
        # @2016/06/08
        _activity['begin_time'] = timestamp_friendly_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
        _activity['end_time'] = timestamp_friendly_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w
        # 价格转换成元
        # _activity['amount'] = float(_activity['amount']) / 100

        order_fees = []
        for ext_fee_id in order['ext_fees']:
            for template in _activity['ext_fee_template']:
                if ext_fee_id == template['_id']:
                    # 价格转换成元
                    _fee = float(template['fee']) / 100
                    json = {"_id":ext_fee_id, "name":template['name'], "fee":_fee}
                    order_fees.append(json)
                    break
        order['fees'] = order_fees

        order_insurances = []
        for insurance_id in order['insurances']:
            _insurance = insurance_template_dao.insurance_template_dao().query(insurance_id)
            order_insurances.append(_insurance)
        order['insurances'] = order_insurances

        # 这里改为从订单中取base_fees
        for base_fee in order['base_fees']:
            # 价格转换成元
            order['activity_amount'] = float(base_fee['fee']) / 100

        order['create_time'] = timestamp_datetime(order['create_time'])

        _old_applys = apply_dao.apply_dao().query_by_order(order_id)
        applyed = False
        if len(_old_applys) > 0:
            applyed = True

        self.render('wx/myorder-info.html',
                vendor_id=vendor_id,
                activity=_activity,
                order=order,
                applyed=applyed)


# 我的微信订单详情页对应的报名信息 @2016/06/13
class WxPcOrderApplyListHandler(tornado.web.RequestHandler):
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        applys = apply_dao.apply_dao().query_by_order(order_id)
        for data in applys:
            try:
                data['note']
            except:
                data['note'] = ''

        self.render('wx/myorder-applys.html',
                vendor_id=vendor_id,
                applys=applys)


class WxPcOrderEvaluateHandler(tornado.web.RequestHandler):
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        _order = order_dao.order_dao().query(order_id)

        self.render('wx/myorder-evaluate.html',
                vendor_id=vendor_id,
                order=_order)

    def post(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)
        _content = self.get_argument("content", "")
        _score = self.get_argument("score", "")
        if _score :
            _score = int(_score)
        else :
            _score = 0

        order = order_dao.order_dao().query(order_id)
        activity_id = order['activity_id']
        activity = activity_dao.activity_dao().query(activity_id)
        triprouter_id = activity['triprouter']

        # 更新订单状态
        json = {'_id':order_id, 'status': ORDER_STATUS_BF_COMMENT}
        order_dao.order_dao().update(json)

        # 创建新的评论
        _id = str(uuid.uuid1()).replace('-', '')
        json = {"_id":_id, "vendor_id":vendor_id,
                "content":_content, "score":_score,
                 "activity":activity_id, "triprouter":triprouter_id}
        evaluation_dao.evaluation_dao().create(json)
        logging.info("create eval _id %r", _id)

        # 更新线路表的评分 先取出该线路的所有评分算平均值后更新
        triprouter = trip_router_dao.trip_router_dao().query(triprouter_id)
        evaluations = evaluation_dao.evaluation_dao().query_by_triprouter(triprouter_id)

        total_score = 0
        total_time = 0

        for evaluation in evaluations:
            total_score = total_score + evaluation['score']
            total_time = total_time + 1
        new_score = math.ceil(float(total_score) / total_time)
        logging.info("create new score %r", new_score)

        _json = {"_id":triprouter_id, "score":int(new_score)}

        trip_router_dao.trip_router_dao().update(_json)

        self.redirect('/bf/wx/vendors/' + vendor_id + '/pc')


class WxPcOrderRepayHandler(tornado.web.RequestHandler):
    def get(self):
        vendor_id = self.get_argument("vendor_id", "")
        logging.info("got vendor_id %r", vendor_id)
        order_id = self.get_argument("order_id", "")
        logging.info("got order_id %r", order_id)

        _old_order = order_dao.order_dao().query(order_id)
        # 查询过去是否填报，有则跳过此步骤。主要是防止用户操作回退键，重新回到此页面
        if _old_order['status'] > 20 and _old_order['status'] != 31:
            return
        else:
            _activity = activity_dao.activity_dao().query(_old_order['activity_id'])
            # FIXME, 将服务模板转为字符串，客户端要用
            _servTmpls = _activity['ext_fee_template']
            _activity['json_serv_tmpls'] = tornado.escape.json_encode(_servTmpls);
            _activity['begin_time'] = timestamp_friendly_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
            _activity['end_time'] = timestamp_friendly_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w
            # 金额转换成元
            # _activity['amount'] = float(_activity['amount']) / 100
            # 金额转换成元
            if not _old_order['base_fees']:
                _old_order['activity_amount'] = 0
            else:
                for base_fee in _old_order['base_fees']:
                    # 价格转换成元
                    _old_order['activity_amount'] = float(base_fee['fee']) / 100

            _timestamp = (int)(_old_order['create_time'])
            prepay_id = _old_order['prepay_id']
            key = WX_MCH_KEY
            nonceB = getNonceStr();
            logging.info("got nonceB %r", nonceB)
            signB = getPaySign(_timestamp, WX_APP_ID, nonceB, prepay_id, key)
            _order_return = {'timestamp': _timestamp,
                    'nonce_str': nonceB,
                    'prepay_id': prepay_id,
                    'pay_sign': signB,
                    'app_id': WX_APP_ID,
                    'return_msg': 'OK'}

            self.render('wx/order-confirm.html',
                vendor_id=vendor_id,
                return_msg='', order_return=_order_return,
                activity=_activity,
                order=_old_order)


# 我的历史积分列表页
class WxPcBonusListHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        account_id = self.get_secure_cookie("account_id")

        _customer_profile = vendor_member_dao.vendor_member_dao().query(vendor_id, account_id)

        _before = time.time()
        _vendor_bonus = bonus_dao.bonus_dao().query_pagination_by_vendor(vendor_id, account_id, _before, PAGE_SIZE_LIMIT)
        for _bonus in _vendor_bonus:
            if _bonus['type'] == 1: # shared activity
                _activity = activity_dao.activity_dao().query(_bonus['res_id'])
                _bonus['title'] = _activity['title']
                _bonus['bk_img_url'] = _activity['bk_img_url']
            elif _bonus['type'] == 3: # buy activity
                _activity = activity_dao.activity_dao().query(_bonus['group_id'])
                _bonus['title'] = _activity['title']
                _bonus['bk_img_url'] = _activity['bk_img_url']
            _bonus['create_time'] = timestamp_datetime(_bonus['create_time'])
            logging.info("got bonus type %r", _bonus['type'])

        self.render('wx/my-bonus.html',
                vendor_id=vendor_id,
                bonus_num=_customer_profile['bonus'],
                vendor_bonus=_vendor_bonus)


# 我的证书列表页
class WxPcCertListHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        _account_id = self.get_secure_cookie("account_id")

        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _account_id)
        if not _customer_profile:
            _customer_profile = {"crets":0}
        else:
            try:
                _customer_profile['crets']
            except:
                _customer_profile['crets'] = 0

        _before = time.time()
        _crets = cret_dao.cret_dao().query_pagination_by_account(vendor_id, _account_id, _before, PAGE_SIZE_LIMIT)
        for _cret in _crets:
            _cret['create_time'] = timestamp_friendly_date(_cret['create_time'])
            _activity = activity_dao.activity_dao().query(_cret['activity_id'])
            _cret['activity_title'] = _activity['title']
            _cret['activity_bk_img_url'] = _activity['bk_img_url']

        self.render('wx/my-certs.html',
                vendor_id=vendor_id,
                crets=_crets,
                customer_profile=_customer_profile)


# 证书详情页
class WxPcCertInfoHandler(tornado.web.RequestHandler):
    def get(self, vendor_id, cret_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got cret_id %r in uri", cret_id)

        _cret = cret_dao.cret_dao().query(cret_id)
        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _cret['account_id'])
        _activity = activity_dao.activity_dao().query(_cret['activity_id'])
        _cret['activity_title'] = _activity['title']

        self.render('wx/cert-info.html',
                vendor_id=vendor_id,
                cret=_cret,
                profile=_customer_profile)


# 我的任务列表页
class WxPcTaskListHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        account_id = self.get_secure_cookie("account_id")
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        personal_tasks = personal_task_dao.personal_task_dao().query_by_vendor_account(vendor_id,account_id)

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

        self.render('wx/my-tasks.html',
                vendor_id=vendor_id,
                tasks=personal_tasks)
