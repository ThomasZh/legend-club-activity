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
from dao import bonus_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import vendor_member_dao
from dao import voucher_dao
from dao import insurance_template_dao
from dao import contact_dao
from dao import vendor_hha_dao
from dao import voucher_pay_dao
from dao import vendor_wx_dao
from dao import voucher_order_dao
from dao import trip_router_dao
from dao import triprouter_share_dao
from dao import club_dao
from dao import activity_share_dao

from auth import auth_email
from auth import auth_phone

from wx_wrap import getAccessTokenByClientCredential
from wx_wrap import getJsapiTicket
from wx_wrap import Sign
from wx_wrap import getNonceStr
from wx_wrap import getOrderSign
from wx_wrap import getPaySign
from wx_wrap import getAccessToken
from wx_wrap import getUserInfo
from xml_parser import parseWxOrderReturn, parseWxPayReturn
from global_const import *



# 活动首页
class WxActivityListHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        _now = time.time()
        # 查询结果，不包含隐藏的活动
        _array = activity_dao.activity_dao().query_not_hidden_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_RECRUIT, _now, PAGE_SIZE_LIMIT)
        logging.info("got activity>>>>>>>>> %r",len(_array))

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
        if len(_array) > 0 :
            for _activity in _array:
                _member_min = int(_activity['member_min'])
                _member_max = int(_activity['member_max'])
                if _now > _activity['end_time']:
                    _activity['phase'] = '3'
                else:
                    _applicant_num = apply_dao.apply_dao().count_by_activity(_activity['_id'])
                    _activity['phase'] = '2' if _applicant_num >= _member_max else '1'
                    _activity['phase'] = '0' if _applicant_num < _member_min else '1'
                # 格式化显示时间
                _activity['begin_time'] = timestamp_friendly_date(_activity['begin_time']) # timestamp -> %m月%d 星期%w
                _activity['end_time'] = timestamp_friendly_date(_activity['end_time']) # timestamp -> %m月%d 星期%w
                # 金额转换成元
                if not _activity['base_fee_template']:
                    _activity['amount'] = 0
                else:
                    for base_fee_template in _activity['base_fee_template']:
                        _activity['amount'] = float(base_fee_template['fee']) / 100
                        break

        self.render('wx/activity-index.html',
                vendor_id=vendor_id,
                activitys=_array)


#推荐活动列表
class WxRecommendActivityHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        _now = time.time()
        # # 查询结果，不包含隐藏的活动
        # _array = [activity_dao.activity_dao().query_activitys_notme(
        #         vendor_id, ACTIVITY_STATUS_RECRUIT, _now, PAGE_SIZE_LIMIT)]
        _array = []

        activitys_share = activity_share_dao.activity_share_dao().query_by_vendor(vendor_id)
        for activity in activitys_share:
            _id = activity['activity']
            arr = activity_dao.activity_dao().query(_id)
            _array.append(arr)

        logging.info("got recommend activity>>>>>>>>> %r",_array)

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
        if len(_array) > 0 :
            for _activity in _array:
                _member_min = int(_activity['member_min'])
                _member_max = int(_activity['member_max'])
                if _now > _activity['end_time']:
                    _activity['phase'] = '3'
                else:
                    _applicant_num = apply_dao.apply_dao().count_by_activity(_activity['_id'])
                    _activity['phase'] = '2' if _applicant_num >= _member_max else '1'
                    _activity['phase'] = '0' if _applicant_num < _member_min else '1'
                # 格式化显示时间
                _activity['begin_time'] = timestamp_friendly_date(_activity['begin_time']) # timestamp -> %m月%d 星期%w
                _activity['end_time'] = timestamp_friendly_date(_activity['end_time']) # timestamp -> %m月%d 星期%w
                # 金额转换成元
                if not _activity['base_fee_template']:
                    _activity['amount'] = 0
                else:
                    for base_fee_template in _activity['base_fee_template']:
                        _activity['amount'] = float(base_fee_template['fee']) / 100
                        break

        self.render('wx/recommend-activity.html',
                vendor_id=vendor_id,
                activitys=_array)


# 推荐活动详情
class WxRecommendActivityInfoHandler(BaseHandler):
    def get(self, vendor_id, activity_id, guest_club_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)
        logging.info("got guest_club_id %r in uri", guest_club_id)

        _activity = activity_dao.activity_dao().query(activity_id)

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
        logging.info("got _member_min %r in uri", _member_min)
        logging.info("got _member_max %r in uri", _member_max)

        if _now > _activity['end_time']:
            _activity['phase'] = '3'
        else:
            _applicant_num = apply_dao.apply_dao().count_by_activity(_activity['_id'])
            logging.info("got _applicant_num %r in uri", _applicant_num)
            _activity['phase'] = '2' if _applicant_num >= _member_max else '1'
            _activity['phase'] = '0' if _applicant_num < _member_min else '1'

        # 格式化时间显示
        _activity['begin_time'] = timestamp_friendly_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
        _activity['end_time'] = timestamp_friendly_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w

        # 金额转换成元 默认将第一个基本服务的费用显示为活动价格
        # _activity['amount'] = float(_activity['amount']) / 100
        if not _activity['base_fee_template']:
            _activity['amount'] = 0
        else:
            for base_fee_template in _activity['base_fee_template']:
                _activity['amount'] = float(base_fee_template['fee']) / 100
                break

        article = self.get_article(activity_id)

        logging.info("------------------------------------uri: "+self.request.uri)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        logging.info("got wx_app_id %r in uri", wx_app_id)
        wx_app_secret = wx_app_info['wx_app_secret']
        wx_notify_domain = wx_app_info['wx_notify_domain']

        _access_token = getAccessTokenByClientCredential(wx_app_id, wx_app_secret)
        _jsapi_ticket = getJsapiTicket(_access_token)
        _sign = Sign(_jsapi_ticket, wx_notify_domain+self.request.uri).sign()
        logging.info("------------------------------------nonceStr: "+_sign['nonceStr'])
        logging.info("------------------------------------jsapi_ticket: "+_sign['jsapi_ticket'])
        logging.info("------------------------------------timestamp: "+str(_sign['timestamp']))
        logging.info("------------------------------------url: "+_sign['url'])
        logging.info("------------------------------------signature: "+_sign['signature'])

        _account_id = self.get_secure_cookie("account_id")
        _bonus_template = bonus_template_dao.bonus_template_dao().query(_activity['_id'])

        self.render('wx/activity-info.html',
                guest_club_id = guest_club_id,
                vendor_id=vendor_id,
                activity=_activity,
                article=article,
                wx_app_id=wx_app_id,
                wx_notify_domain=wx_notify_domain,
                sign=_sign, account_id=_account_id,
                bonus_template=_bonus_template)


# 活动详情
class WxActivityInfoHandler(BaseHandler):
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)
        _activity = activity_dao.activity_dao().query(activity_id)
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
        logging.info("got _member_min %r in uri", _member_min)
        logging.info("got _member_max %r in uri", _member_max)

        if _now > _activity['end_time']:
            _activity['phase'] = '3'
        else:
            _applicant_num = apply_dao.apply_dao().count_by_activity(_activity['_id'])
            logging.info("got _applicant_num %r in uri", _applicant_num)
            _activity['phase'] = '2' if _applicant_num >= _member_max else '1'
            _activity['phase'] = '0' if _applicant_num < _member_min else '1'

        # 格式化时间显示
        _activity['begin_time'] = timestamp_friendly_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
        _activity['end_time'] = timestamp_friendly_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w

        # 金额转换成元 默认将第一个基本服务的费用显示为活动价格
        # _activity['amount'] = float(_activity['amount']) / 100
        if not _activity['base_fee_template']:
            _activity['amount'] = 0
        else:
            for base_fee_template in _activity['base_fee_template']:
                _activity['amount'] = float(base_fee_template['fee']) / 100
                break

        article = self.get_article(activity_id)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        logging.info("got wx_app_id %r in uri", wx_app_id)
        wx_app_secret = wx_app_info['wx_app_secret']
        wx_notify_domain = wx_app_info['wx_notify_domain']

        logging.info("------------------------------------uri: "+self.request.uri)
        _access_token = getAccessTokenByClientCredential(wx_app_id, wx_app_secret)
        _jsapi_ticket = getJsapiTicket(_access_token)
        _sign = Sign(_jsapi_ticket, wx_notify_domain+self.request.uri).sign()
        logging.info("------------------------------------nonceStr: "+_sign['nonceStr'])
        logging.info("------------------------------------jsapi_ticket: "+_sign['jsapi_ticket'])
        logging.info("------------------------------------timestamp: "+str(_sign['timestamp']))
        logging.info("------------------------------------url: "+_sign['url'])
        logging.info("------------------------------------signature: "+_sign['signature'])

        _account_id = self.get_secure_cookie("account_id")
        _bonus_template = bonus_template_dao.bonus_template_dao().query(_activity['_id'])

        self.render('wx/activity-info.html',
                guest_club_id = GUEST_CLUB_ID,
                vendor_id=vendor_id,
                activity=_activity,
                article=article,
                wx_app_id=wx_app_id,
                wx_notify_domain=wx_notify_domain,
                sign=_sign, account_id=_account_id,
                bonus_template=_bonus_template)


# 活动二维码
class WxActivityQrcodeHandler(tornado.web.RequestHandler):
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        _activity = activity_dao.activity_dao().query(activity_id)
        _qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)
        # 为活动添加二维码属性
        _activity['wx_qrcode_url'] = _qrcode['wx_qrcode_url']
        logging.debug(_qrcode)

        self.render('wx/activity-qrcode.html',
                vendor_id=vendor_id,
                activity=_activity)


class WxActivityApplyStep0Handler(BaseHandler):
    def get(self, vendor_id, activity_id, guest_club_id):

        logging.info("guest_club_id+++++++++++%r",guest_club_id)

        wx_app_id=''
        activity = activity_dao.activity_dao().query(activity_id)
        activity_club = activity['vendor_id']
        # 不是我的活动 直接跳走（此时guest_club_id肯定不是0）
        if vendor_id != activity_club:
            wx_app_info = vendor_wx_dao.vendor_wx_dao().query(guest_club_id)
            wx_notify_domain = wx_app_info['wx_notify_domain']
            redirect_url = wx_notify_domain+"/bf/wx/vendors/"+guest_club_id+"/activitys/"+ activity_id+"_"+ vendor_id +"/apply/step0"
        else:
            wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
            wx_app_id = wx_app_info['wx_app_id']
            wx_notify_domain = wx_app_info['wx_notify_domain']
            logging.info("got wx_app_id %r in uri", wx_app_id)
            redirect_url= "https://open.weixin.qq.com/connect/oauth2/authorize?appid="+ wx_app_id +"&redirect_uri="+ wx_notify_domain +"/bf/wx/vendors/"+vendor_id+"/activitys/"+ activity_id+"_"+ guest_club_id +"/apply/step01&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect"

        # FIXME 这里应改为从缓存取自己的access_token然后查myinfo是否存在wx_openid
        # 存在就直接用，不存在再走微信授权并更新用户信息 /api/myinfo-as-wx-user
        access_token=self.get_secure_cookie("access_token")
        logging.info("access_token %r======", access_token)

        if access_token:
            try:
                url = API_DOMAIN + "/api/myinfo-as-wx-user"
                http_client = HTTPClient()
                headers = {"Authorization":"Bearer "+access_token}
                response = http_client.fetch(url, method="GET", headers=headers)
                logging.info("got response.body %r", response.body)
                user = json_decode(response.body)
                account_id=user['_id']
                avatar=user['avatar']
                nickname=user['nickname']

                self.create_club_user(vendor_id, account_id)

                activity = activity_dao.activity_dao().query(activity_id)
                activity['begin_time'] = timestamp_friendly_date(float(activity['begin_time'])) # timestamp -> %m月%d 星期%w
                activity['end_time'] = timestamp_friendly_date(float(activity['end_time'])) # timestamp -> %m月%d 星期%w

                self.render('wx/activity-apply-step1.html',
                        guest_club_id = guest_club_id,
                        vendor_id=vendor_id,
                        wx_app_id=wx_app_id,
                        activity=activity)
            except:
                self.redirect(redirect_url)
        else:
            self.redirect(redirect_url)


class WxActivityApplyStep01Handler(BaseHandler):
    def get(self, vendor_id, activity_id, guest_club_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        user_agent = self.request.headers["User-Agent"]
        lang = self.request.headers["Accept-Language"]

        wx_code = self.get_argument("code", "")
        logging.info("got wx_code=[%r] from argument", wx_code)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        wx_notify_domain = wx_app_info['wx_notify_domain']
        logging.info("got wx_app_id %r in uri", wx_app_id)
        wx_app_secret = wx_app_info['wx_app_secret']

        if not wx_code:
            redirect_url= "https://open.weixin.qq.com/connect/oauth2/authorize?appid="+ wx_app_id +"&redirect_uri="+ wx_notify_domain +"/bf/wx/vendors/"+vendor_id+"/activitys/"+ activity_id +"_"+ guest_club_id +"/apply/step01&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect"
            self.redirect(redirect_url)
            return

        accessToken = getAccessToken(wx_app_id, wx_app_secret, wx_code);
        access_token = accessToken["access_token"];
        logging.info("got access_token %r", access_token)
        wx_openid = accessToken["openid"];
        logging.info("got wx_openid %r", wx_openid)

        wx_userInfo = getUserInfo(access_token, wx_openid)
        nickname = wx_userInfo["nickname"]
        #nickname = unicode(nickname).encode('utf-8')
        logging.info("got nickname=[%r]", nickname)
        avatar = wx_userInfo["headimgurl"]
        logging.info("got avatar=[%r]", avatar)

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

        url = API_DOMAIN + "/api/auth/wx/register"
        http_client = HTTPClient()
        random = str(uuid.uuid1()).replace('-', '')
        headers = {"Authorization":"Bearer "+random}
        _json = json_encode({'wx_openid':wx_openid,'nickname':nickname,'avatar':avatar})
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        session_ticket = data['rs']
        account_id = session_ticket['account_id']

        self.set_secure_cookie("access_token", session_ticket['access_token'])
        self.set_secure_cookie("expires_at", str(session_ticket['expires_at']))
        self.set_secure_cookie("account_id",account_id)
        # self.set_secure_cookie("wx_openid",wx_openid)
        # self.set_secure_cookie("nickname",nickname)
        # self.set_secure_cookie("avatar",avatar)

        self.create_club_user(vendor_id, account_id)

        self.redirect('/bf/wx/vendors/' + vendor_id + '/activitys/'+activity_id+'_'+guest_club_id+'/apply/step1')


class WxActivityApplyStep1Handler(BaseHandler):
    def get(self, vendor_id, activity_id, guest_club_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        logging.info("got wx_app_id %r in uri", wx_app_id)

        activity = activity_dao.activity_dao().query(activity_id)
        activity['begin_time'] = timestamp_friendly_date(float(activity['begin_time'])) # timestamp -> %m月%d 星期%w
        activity['end_time'] = timestamp_friendly_date(float(activity['end_time'])) # timestamp -> %m月%d 星期%w

        self.render('wx/activity-apply-step1.html',
                guest_club_id = guest_club_id,
                vendor_id=vendor_id,
                wx_app_id=wx_app_id,
                activity=activity)


class WxActivityApplyStep2Handler(AuthorizationHandler):
    def post(self):
        vendor_id = self.get_argument("vendor_id", "")
        logging.info("got vendor_id %r", vendor_id)
        activity_id = self.get_argument("activity_id", "")
        logging.info("got activity_id %r", activity_id)
        _account_id = self.get_secure_cookie("account_id")
        guest_club_id = self.get_argument("guest_club_id")
        logging.info("got guest_club_id %r", guest_club_id)

        access_token = self.get_access_token()

        # 取得自己的最后一笔订单
        params = {"filter":"account", "account_id":_account_id, "page":1, "limit":1,}
        url = url_concat(API_DOMAIN + "/api/orders", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        orders = rs['data']

        _timestamp = time.time()
        # 一分钟内不能创建第二个订单,
        # 防止用户点击回退按钮，产生第二个订单
        if len(orders) > 0:
            for order in orders:
                if (_timestamp - order['create_time']) < 60:
                    self.redirect('/bf/wx/orders/wait')

        # 订单总金额
        _total_amount = self.get_argument("total_amount", 0)
        logging.info("got _total_amount %r", _total_amount)
        # 价格转换成分
        _total_amount = int(float(_total_amount) * 100)
        logging.info("got _total_amount %r", _total_amount)
        # 订单申报数目
        _applicant_num = self.get_argument("applicant_num", 1)
        # 活动金额，即已选的基本服务项金额
        amount = 0
        actual_payment = 0
        quantity = int(_applicant_num)

        _activity = activity_dao.activity_dao().query(activity_id)
        _bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus_points = int(_bonus_template['activity_shared'])

        #基本服务
        _base_fee_ids = self.get_body_argument("base_fees", [])
        logging.info("got _base_fee_ids %r", _base_fee_ids)
        # 转为列表
        _base_fee_ids = JSON.loads(_base_fee_ids)
        _base_fees = []
        base_fee_template = _activity['base_fee_template']
        for _base_fee_id in _base_fee_ids:
            for template in base_fee_template:
                if _base_fee_id == template['_id']:
                    _base_fee = {"_id":_base_fee_id, "name":template['name'], "fee":template['fee']}
                    _base_fees.append(_base_fee)
                    activity_amount = template['fee']
                    amount = amount + template['fee']
                    actual_payment = actual_payment + int(template['fee']) * quantity
                    break;

        # 附加服务项编号数组
        # *** 接受json数组用这个 ***
        _ext_fee_ids = self.get_body_argument("ext_fees", [])
        logging.info("got _ext_fee_ids %r", _ext_fee_ids)
        # 转为列表
        _ext_fee_ids = JSON.loads(_ext_fee_ids)
        _ext_fees = []
        ext_fee_template = _activity['ext_fee_template']
        for _ext_fee_id in _ext_fee_ids:
            for template in ext_fee_template:
                if _ext_fee_id == template['_id']:
                    _ext_fee = {"_id":_ext_fee_id, "name":template['name'], "fee":template['fee']}
                    _ext_fees.append(_ext_fee)
                    amount = amount + template['fee']
                    actual_payment = actual_payment + int(template['fee']) * quantity
                    break;

        # 保险选项,数组
        _insurance_ids = self.get_body_argument("insurances", [])
        _insurance_ids = JSON.loads(_insurance_ids)
        _insurances = []
        _insurance_templates = insurance_template_dao.insurance_template_dao().query_by_vendor(vendor_id)
        for _insurance_id in _insurance_ids:
            for _insurance_template in _insurance_templates:
                if _insurance_id == _insurance_template['_id']:
                    _insurance = {"_id":_insurance_id, "name":_insurance_template['title'], "fee":_insurance_template['amount']}
                    _insurances.append(_insurance)
                    amount = amount + _insurance['fee']
                    actual_payment = actual_payment + int(_insurance['fee']) * quantity
                    break;

        #代金券选项,数组
        _vouchers_ids = self.get_body_argument("vouchers", [])
        _vouchers_ids = JSON.loads(_vouchers_ids)
        _vouchers = []
        for _vouchers_id in _vouchers_ids:
            logging.info("got _vouchers_id %r", _vouchers_id)
            _voucher = voucher_dao.voucher_dao().query_not_safe(_vouchers_id)
            _json = {'_id':_vouchers_id, 'fee':_voucher['amount']}
            _vouchers.append(_json)
            actual_payment = actual_payment - int(_json['fee'])

        # 积分选项,数组
        _bonus = 0
        _bonus_array = self.get_body_argument("bonus", [])
        if _bonus_array:
            _bonus_array = JSON.loads(_bonus_array)
            if len(_bonus_array) > 0:
                _bonus = _bonus_array[0]
                # 价格转换成分
                _bonus = - int(float(_bonus) * 100)
        logging.info("got _bonus %r", _bonus)
        points = _bonus
        actual_payment = actual_payment + points

        _order_id = str(uuid.uuid1()).replace('-', '')
        _status = ORDER_STATUS_BF_INIT
        if actual_payment == 0:
            _status = ORDER_STATUS_WECHAT_PAY_SUCCESS

        # 创建订单索引
        order_index = {
            "_id": _order_id,
            "order_type": "buy_activity",
            "club_id": vendor_id,
            "item_type": "activity",
            "item_id": activity_id,
            "item_name": _activity['title'],
            "distributor_type": "club",
            "distributor_id": guest_club_id,
            "create_time": _timestamp,
            "pay_type": "wxpay",
            "pay_status": _status,
            "quantity": quantity,
            "amount": amount, #已经转换为分，注意转为数值
            "actual_payment": actual_payment, #已经转换为分，注意转为数值
            "base_fees": _base_fees,
            "ext_fees": _ext_fees,
            "insurances": _insurances,
            "vouchers": _vouchers,
            "points_used": points,
            "bonus_points": bonus_points, # 活动奖励积分
        }
        self.create_order(order_index)

        # budge_num increase
        self.counter_increase(vendor_id, "activity_order")
        self.counter_increase(activity_id, "order")
        # TODO notify this message to vendor's administrator by SMS

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        logging.info("got wx_app_id %r in uri", wx_app_id)
        wx_mch_key = wx_app_info['wx_mch_key']
        wx_mch_id = wx_app_info['wx_mch_id']
        wx_notify_domain = wx_app_info['wx_notify_domain']

        _timestamp = (int)(time.time())
        if _total_amount != 0:
            # wechat 统一下单
            # _openid = self.get_secure_cookie("wx_openid")
            # logging.info("got _openid %r", _openid)
            # 从comm中统一取
            myinfo = self.get_myinfo_login()
            _openid = myinfo['login']

            _store_id = 'Aplan'
            logging.info("got _store_id %r", _store_id)
            _product_description = _activity['title']
            logging.info("got _product_description %r", _product_description)

            key = wx_mch_key
            nonceA = getNonceStr();
            logging.info("got nonceA %r", nonceA)
            #_ip = self.request.remote_ip
            _remote_ip = self.request.headers['X-Real-Ip']
            logging.info("got _remote_ip %r", _remote_ip)
            total_fee = str(_total_amount)
            logging.info("got total_fee %r", total_fee)
            notify_url = wx_notify_domain + '/bf/wx/orders/notify'
            logging.info("got notify_url %r", notify_url)
            signA = getOrderSign(_remote_ip, notify_url, wx_app_id, wx_mch_id, nonceA, _openid, key, _store_id, _order_id, _product_description, total_fee)
            logging.info("got signA %r", signA)

            _xml = '<xml>' \
                + '<appid>' + wx_app_id + '</appid>' \
                + '<attach>' + _store_id + '</attach>' \
                + '<body>' + _product_description + '</body>' \
                + '<mch_id>' + wx_mch_id + '</mch_id>' \
                + '<nonce_str>' + nonceA + '</nonce_str>' \
                + '<notify_url>' + notify_url + '</notify_url>' \
                + '<openid>' + _openid + '</openid>' \
                + '<out_trade_no>' + _order_id + '</out_trade_no>' \
                + '<spbill_create_ip>' + _remote_ip + '</spbill_create_ip>' \
                + '<total_fee>' + str(_total_amount) + '</total_fee>' \
                + '<trade_type>JSAPI</trade_type>' \
                + '<sign>' + signA + '</sign>' \
                + '</xml>'
            url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_xml)
            logging.info("got response %r", response.body)
            _order_return = parseWxOrderReturn(response.body)

            logging.info("got _timestamp %r", str(_timestamp))
            try:
                prepayId = _order_return['prepay_id']
            except:
                _order_return['prepay_id'] = ''
                prepayId = ''
            logging.info("got prepayId %r", prepayId)
            try:
                nonceB = _order_return['nonce_str']
            except:
                _order_return['nonce_str'] = ''
                nonceB = ''
            signB = getPaySign(_timestamp, wx_app_id, nonceB, prepayId, key)
            logging.info("got signB %r", signB)
            _order_return['pay_sign'] = signB
            _order_return['timestamp'] = _timestamp
            _order_return['app_id'] = wx_app_id

            # 微信统一下单返回成功
            order_unified = None
            if(_order_return['return_msg'] == 'OK'):
                order_unified = {'_id':_order_id,'prepay_id': prepayId, 'pay_status': ORDER_STATUS_WECHAT_UNIFIED_SUCCESS}
            else:
                order_unified = {'_id':_order_id,'prepay_id': prepayId, 'pay_status': ORDER_STATUS_WECHAT_UNIFIED_FAILED}
            # 微信统一下单返回成功
            # TODO: 更新订单索引中，订单状态pay_status,prepay_id
            self.update_order_unified(order_unified)

            # FIXME, 将服务模板转为字符串，客户端要用
            _servTmpls = _activity['ext_fee_template']
            _activity['json_serv_tmpls'] = tornado.escape.json_encode(_servTmpls);
            _activity['begin_time'] = timestamp_friendly_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
            _activity['end_time'] = timestamp_friendly_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w
            # 金额转换成元
            # _activity['amount'] = float(activity_amount) / 100
            for base_fee in order_index['base_fees']:
                # 价格转换成元
                order_index['activity_amount'] = float(base_fee['fee']) / 100

            self.render('wx/order-confirm.html',
                    vendor_id=vendor_id,
                    return_msg=response.body, order_return=_order_return,
                    activity=_activity, order_index=order_index)
        else: #_total_amount == 0:
            # FIXME, 将服务模板转为字符串，客户端要用
            _servTmpls = _activity['ext_fee_template']
            _activity['json_serv_tmpls'] = tornado.escape.json_encode(_servTmpls);
            _activity['begin_time'] = timestamp_friendly_date(float(_activity['begin_time'])) # timestamp -> %m月%d 星期%w
            _activity['end_time'] = timestamp_friendly_date(float(_activity['end_time'])) # timestamp -> %m月%d 星期%w
            # 金额转换成元
            # _activity['amount'] = float(activity_amount) / 100
            for base_fee in order_index['base_fees']:
                # 价格转换成元
                order_index['activity_amount'] = float(base_fee['fee']) / 100

            # 如使用积分抵扣，则将积分减去
            if order_index['points_used'] < 0:
                # 修改个人积分信息
                self.points_increase(vendor_id, order_index['account_id'], order_index['points_used'])

            # 如使用代金券抵扣，则将代金券减去
            for _voucher in _vouchers:
                # status=2, 已使用
                voucher_dao.voucher_dao().update({'_id':_voucher['_id'], 'status':2, 'last_update_time':_timestamp})
                _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, order_index['account_id'])
                # 修改个人代金券信息
                _voucher_amount = int(_customer_profile['vouchers']) - int(_voucher['fee'])
                if _voucher_amount < 0:
                    _voucher_amount = 0
                _json = {'vendor_id':vendor_id, 'account_id':order_index['account_id'], 'last_update_time':_timestamp,
                        'vouchers':_voucher_amount}
                vendor_member_dao.vendor_member_dao().update(_json)

            self.render('wx/order-confirm.html',
                    vendor_id=vendor_id,
                    return_msg='OK',
                    order_return={'timestamp':_timestamp,
                        'nonce_str':'',
                        'pay_sign':'',
                        'prepay_id':'',
                        'app_id': wx_app_id,
                        'return_msg':'OK'},
                    activity=_activity,
                    order_index=order_index)


# 添加当前订单的成员
class WxActivityApplyStep3Handler(AuthorizationHandler):
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        _order_id = self.get_argument("order_id", "")
        logging.info("got _order_id %r", _order_id)

        _activity = activity_dao.activity_dao().query(activity_id)

        # FIXME, 返回账号给前端，用来ajax查询当前用户的联系人
        # @2016/06/14
        _account_id = self.get_secure_cookie("account_id")

        self.render('wx/activity-apply-step3.html',
                vendor_id=vendor_id,
                activity=_activity,
                order_id=_order_id,
                account_id=_account_id)


    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        _account_id = self.get_secure_cookie("account_id")
        _order_id = self.get_argument("order_id", "")

        # 查询过去是否填报，有则跳过此步骤。主要是防止用户操作回退键，重新回到此页面
        _old_order = self.get_symbol_object(_order_id)
        if _old_order['pay_status'] > 30:
            _activity = activity_dao.activity_dao().query(activity_id)
            _qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)
            # 为活动添加二维码属性
            _activity['wx_qrcode_url'] = _qrcode['wx_qrcode_url']
            logging.info(_qrcode)
            self.render('wx/activity-apply-step3.html',
                    vendor_id=vendor_id,
                    activity=_activity,
                    order_id=_order_id,
                    account_id=_account_id)
            return
        else:
            _activity = activity_dao.activity_dao().query(activity_id)

            _applicantstr = self.get_body_argument("applicants", [])
            _applicantList = JSON.loads(_applicantstr);
            # 处理多个申请人
            for apply_index in _applicantList:
                apply_index["club_id"] = vendor_id
                apply_index["item_type"] = "activity"
                apply_index["item_id"] = activity_id
                apply_index["item_name"] = _activity['title']
                apply_index["order_id"] = _order_id
                apply_index["booking_time"] = _activity['begin_time']
                # 取活动基本服务费用信息
                apply_index["group_name"] = _old_order['base_fees'][0]['name']
                apply_id = self.create_apply(apply_index)

                # budge_num increase
                self.counter_increase(vendor_id, "activity_apply")
                self.counter_increase(activity_id, "apply")
                # TODO notify this message to vendor's administrator by SMS

                # 更新联系人资料
                _contact = contact_dao.contact_dao().query_contact(vendor_id, _account_id, apply_index["real_name"])
                if not _contact: # 如果不存在
                    apply_index["_id"] = apply_id
                    # 移除多余的参数直接入库
                    apply_index.pop("item_id", None)
                    apply_index.pop("order_id", None)
                    contact_dao.contact_dao().create(apply_index)
                else: # 用新资料更新
                    apply_index["_id"] = _contact["_id"]
                    contact_dao.contact_dao().update(apply_index)

            _bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
            _qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)
            # 为活动添加二维码属性
            _activity['wx_qrcode_url'] = _qrcode['wx_qrcode_url']
            logging.info(_qrcode)
            self.render('wx/activity-apply-step4.html',
                    vendor_id=vendor_id,
                    activity=_activity,
                    bonus_template=_bonus_template)


# 微信支付结果通用通知
# 该链接是通过【统一下单API】中提交的参数notify_url设置，如果链接无法访问，商户将无法接收到微信通知。
# 通知url必须为直接可访问的url，不能携带参数。示例：notify_url：“https://pay.weixin.qq.com/wxpay/pay.action”
class WxOrderNotifyHandler(BaseHandler):
    def post(self):
        # 返回参数
        #<xml>
        # <appid><![CDATA[wxaa328c83d3132bfb]]></appid>\n
        # <attach><![CDATA[Aplan]]></attach>\n
        # <bank_type><![CDATA[CFT]]></bank_type>\n
        # <cash_fee><![CDATA[1]]></cash_fee>\n
        # <fee_type><![CDATA[CNY]]></fee_type>\n
        # <is_subscribe><![CDATA[Y]]></is_subscribe>\n
        # <mch_id><![CDATA[1340430801]]></mch_id>\n
        # <nonce_str><![CDATA[jOhHjqDfx9VQGmU]]></nonce_str>\n
        # <openid><![CDATA[oy0Kxt7zNpZFEldQmHwFF-RSLNV0]]></openid>\n
        # <out_trade_no><![CDATA[e358738e30fe11e69a7e00163e007b3e]]></out_trade_no>\n
        # <result_code><![CDATA[SUCCESS]]></result_code>\n
        # <return_code><![CDATA[SUCCESS]]></return_code>\n
        # <sign><![CDATA[6291D73149D05F09D18C432E986C4DEB]]></sign>\n
        # <time_end><![CDATA[20160613083651]]></time_end>\n
        # <total_fee>1</total_fee>\n
        # <trade_type><![CDATA[JSAPI]]></trade_type>\n
        # <transaction_id><![CDATA[4007652001201606137183943151]]></transaction_id>\n
        #</xml>
        _xml = self.request.body
        logging.info("got return_body %r", _xml)
        _pay_return = parseWxPayReturn(_xml)

        logging.info("got result_code %r", _pay_return['result_code'])
        logging.info("got total_fee %r", _pay_return['total_fee'])
        logging.info("got time_end %r", _pay_return['time_end'])
        logging.info("got transaction_id %r", _pay_return['transaction_id'])
        logging.info("got out_trade_no %r", _pay_return['out_trade_no'])

        _order_id = _pay_return['out_trade_no']
        _result_code = _pay_return['result_code']
        if _result_code == 'SUCCESS' :
            # 查询过去是否填报，有则跳过此步骤。主要是防止用户操作回退键，重新回到此页面
            order_index = self.get_order_index(_order_id)
            # 用于更新积分、优惠券
            vendor_id = order_index['club_id']
            if order_index['pay_status'] == 30:
                return
            else:
                # 调用微信支付接口，返回成功
                # TODO: 更新订单索引中，订单状态pay_status,transaction_id,payed_total_fee
                order_payed = {
                    '_id':_order_id,
                    "pay_status": ORDER_STATUS_WECHAT_PAY_SUCCESS,
                    'transaction_id':_pay_return['transaction_id'],
                    'actual_payment':_pay_return['total_fee']
                }
                self.update_order_payed(order_payed)

                order = self.get_symbol_object(_order_id)
                # 如使用积分抵扣，则将积分减去
                _bonus = order['bonus']
                if _bonus < 0:
                    # 修改个人积分信息
                    self.points_increase(vendor_id, order_index['account_id'], bonus)

                # 如使用代金券抵扣，则将代金券减去
                _vouchers = order['vouchers']
                for _voucher in _vouchers:
                    # status=2, 已使用
                    voucher_dao.voucher_dao().update({'_id':_voucher['_id'], 'status':2, 'last_update_time':_timestamp})
                    _customer_profile = mongodao().query_vendor_member_not_safe(vendor_id, order['account_id'])
                    # 修改个人代金券信息
                    _voucher_amount = int(_customer_profile['vouchers']) - int(_voucher['fee'])
                    if _voucher_amount < 0:
                        _voucher_amount = 0
                    _json = {'vendor_id':vendor_id, 'account_id':order['account_id'], 'last_update_time':_timestamp,
                        'vouchers':_voucher_amount}
                    vendor_member_dao.vendor_member_dao().update(_json)
        else:
            # 调用微信支付接口，返回成功
            # TODO: 更新订单索引中，订单状态pay_status,transaction_id,payed_total_fee
            order_payed = {'_id':_order_id,
                "pay_status": ORDER_STATUS_WECHAT_PAY_FAILED,
                'transaction_id':DEFAULT_USER_ID,
                'actual_payment':0}
            self.update_order_payed(order_payed)


class WxOrderWaitHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info("wait for a moments")

        self.render('wx/orders-wait.html')


# 添加当前订单的成员
class WxHhaHandler(tornado.web.RequestHandler):
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        vendor_hha = vendor_hha_dao.vendor_hha_dao().query(vendor_id)

        self.render('wx/hold-harmless-agreements.html',
                vendor_id=vendor_id,
                vendor_hha=vendor_hha)


# 显示分享的代金券页面 可购买
class WxVoucherShareHandler(tornado.web.RequestHandler):
    def get(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        voucher = voucher_pay_dao.voucher_pay_dao().query_not_safe(voucher_id)
        voucher['amount'] = float(voucher['amount']) / 100
        voucher['price'] = float(voucher['price']) / 100
        vendor_wx = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = vendor_wx['wx_app_id']
        wx_app_secret=vendor_wx['wx_app_secret']
        wx_notify_domain = wx_app_info['wx_notify_domain']

        logging.info("------------------------------------uri: "+self.request.uri)
        _access_token = getAccessTokenByClientCredential(wx_app_id, wx_app_secret)
        _jsapi_ticket = getJsapiTicket(_access_token)
        _sign = Sign(_jsapi_ticket, wx_notify_domain+self.request.uri).sign()
        logging.info("------------------------------------nonceStr: "+_sign['nonceStr'])
        logging.info("------------------------------------jsapi_ticket: "+_sign['jsapi_ticket'])
        logging.info("------------------------------------timestamp: "+str(_sign['timestamp']))
        logging.info("------------------------------------url: "+_sign['url'])
        logging.info("------------------------------------signature: "+_sign['signature'])


        _account_id = self.get_secure_cookie("account_id")

        self.render('wx/voucher-pay-info.html',
                vendor_id=vendor_id,
                voucher=voucher,
                wx_app_id=wx_app_id,
                wx_notify_domain=wx_notify_domain,
                sign=_sign, account_id=_account_id,
                vendor_wx=vendor_wx)


# 微信支付结果通用通知
# 该链接是通过【统一下单API】中提交的参数notify_url设置，如果链接无法访问，商户将无法接收到微信通知。
# 通知url必须为直接可访问的url，不能携带参数。示例：notify_url：“https://pay.weixin.qq.com/wxpay/pay.action”
class WxVoucherOrderNotifyHandler(tornado.web.RequestHandler):
    def post(self):
        # 返回参数
        #<xml>
        # <appid><![CDATA[wxaa328c83d3132bfb]]></appid>\n
        # <attach><![CDATA[Aplan]]></attach>\n
        # <bank_type><![CDATA[CFT]]></bank_type>\n
        # <cash_fee><![CDATA[1]]></cash_fee>\n
        # <fee_type><![CDATA[CNY]]></fee_type>\n
        # <is_subscribe><![CDATA[Y]]></is_subscribe>\n
        # <mch_id><![CDATA[1340430801]]></mch_id>\n
        # <nonce_str><![CDATA[jOhHjqDfx9VQGmU]]></nonce_str>\n
        # <openid><![CDATA[oy0Kxt7zNpZFEldQmHwFF-RSLNV0]]></openid>\n
        # <out_trade_no><![CDATA[e358738e30fe11e69a7e00163e007b3e]]></out_trade_no>\n
        # <result_code><![CDATA[SUCCESS]]></result_code>\n
        # <return_code><![CDATA[SUCCESS]]></return_code>\n
        # <sign><![CDATA[6291D73149D05F09D18C432E986C4DEB]]></sign>\n
        # <time_end><![CDATA[20160613083651]]></time_end>\n
        # <total_fee>1</total_fee>\n
        # <trade_type><![CDATA[JSAPI]]></trade_type>\n
        # <transaction_id><![CDATA[4007652001201606137183943151]]></transaction_id>\n
        #</xml>
        _xml = self.request.body
        logging.info("got return_body %r", _xml)
        _pay_return = parseWxPayReturn(_xml)

        logging.info("got result_code %r", _pay_return['result_code'])
        logging.info("got total_fee %r", _pay_return['total_fee'])
        logging.info("got time_end %r", _pay_return['time_end'])
        logging.info("got transaction_id %r", _pay_return['transaction_id'])
        logging.info("got out_trade_no %r", _pay_return['out_trade_no'])

        _order_id = _pay_return['out_trade_no']
        _result_code = _pay_return['result_code']
        if _result_code == 'SUCCESS' :
            # 查询过去是否填报，有则跳过此步骤。主要是防止用户操作回退键，重新回到此页面
            _old_order = voucher_order_dao.voucher_order_dao().query(_order_id)
            if _old_order['status'] > 30:
                return
            else:
                _timestamp = int(time.time())
                json = {'_id':_order_id,
                    'last_update_time': _timestamp, "status": ORDER_STATUS_WECHAT_PAY_SUCCESS,
                    'transaction_id':_pay_return['transaction_id'], 'payed_total_fee':_pay_return['total_fee']}
                voucher_order_dao.voucher_order_dao().update(json)

        else:
            _timestamp = (int)(time.time())
            json = {'_id':_order_id,
                'last_update_time': _timestamp, "status": ORDER_STATUS_WECHAT_PAY_FAILED}
            voucher_order_dao.voucher_order_dao().update(json)


# 点击购买优惠券 先检查用户 再创建订单 然后返回确认再微信支付 最后提示成功
class WxVoucherBuyStep0Handler(tornado.web.RequestHandler):
    def get(self, vendor_id, voucher_id):
        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        wx_notify_domain = wx_app_info['wx_notify_domain']

        logging.info("got wx_app_id %r in uri", wx_app_id)

        redirect_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + wx_app_id + "&redirect_uri=" + wx_notify_domain + "/bf/wx/vendors/" + vendor_id + "/vouchers/"+voucher_id+"/buy/step1&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect"
        # FIXME 这里应改为从缓存取自己的access_token然后查myinfo是否存在wx_openid
        # 存在就直接用，不存在再走微信授权并更新用户信息 /api/myinfo-as-wx-user
        access_token=self.get_secure_cookie("access_token")
        logging.info("access_token %r======", access_token)

        if access_token:
            try:
                url = API_DOMAIN + "/api/myinfo-as-wx-user"
                http_client = HTTPClient()
                headers = {"Authorization":"Bearer "+access_token}
                response = http_client.fetch(url, method="GET", headers=headers)
                logging.info("got response.body %r", response.body)
                data = json_decode(response.body)
                user = data['rs']
                account_id=user['_id']
                avatar=user['avatar']
                nickname=user['nickname']

                timestamp = time.time()
                vendor_member = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, account_id)
                if not vendor_member:
                    memeber_id = str(uuid.uuid1()).replace('-', '')
                    _json = {'_id':memeber_id, 'vendor_id':vendor_id,
                        'account_id':account_id, 'account_nickname':nickname, 'account_avatar':avatar,
                        'comment':'...',
                        'bonus':0, 'history_bonus':0, 'vouchers':0, 'crets':0,
                        'rank':0, 'tour_leader':False,
                        'distance':0,
                        'create_time':timestamp, 'last_update_time':timestamp}
                    vendor_member_dao.vendor_member_dao().create(_json)
                    logging.info("create vendor member %r", account_id)
                else:
                    _json = {'vendor_id':vendor_id,
                        'account_id':account_id, 'account_nickname':nickname, 'account_avatar':avatar,
                        'last_update_time':timestamp}
                    vendor_member_dao.vendor_member_dao().update(_json)

                _voucher = voucher_pay_dao.voucher_pay_dao().query_not_safe(voucher_id);
                _voucher['amount'] = float(_voucher['amount']) / 100
                _voucher['price'] = float(_voucher['price']) / 100

                vendor_member = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, account_id)
                if(vendor_member):
                    try:
                        vendor_member['account_nickname']
                    except:
                        vendor_member['account_nickname'] = ''
                    try:
                        vendor_member['account_avatar']
                    except:
                        vendor_member['account_avatar'] = ''
                _avatar = vendor_member['account_avatar']
                _nickname = vendor_member['account_nickname']

                self.render('wx/voucher-order-confirm.html',
                        vendor_id=vendor_id,
                        voucher=_voucher)

            except:
                self.redirect(redirect_url)
        else:
            self.redirect(redirect_url)


class WxVoucherBuyStep1Handler(tornado.web.RequestHandler):
    def get(self, vendor_id, voucher_id):

        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)
        user_agent = self.request.headers["User-Agent"]
        lang = self.request.headers["Accept-Language"]

        wx_code = self.get_argument("code", "")
        logging.info("got wx_code=[%r] from argument", wx_code)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        logging.info("got wx_app_id %r in uri", wx_app_id)
        wx_app_secret = wx_app_info['wx_app_secret']
        wx_notify_domain = wx_app_info['wx_notify_domain']

        if not wx_code:
            redirect_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + wx_app_id + "&redirect_uri=" + wx_notify_domain + "/bf/wx/vendors/" + vendor_id + "/vouchers/"+voucher_id+"/buy/step1&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect"
            self.redirect(redirect_url)
            return

        accessToken = getAccessToken(wx_app_id, wx_app_secret, wx_code);
        access_token = accessToken["access_token"];
        logging.info("got access_token %r", access_token)
        wx_openid = accessToken["openid"];
        logging.info("got wx_openid %r", wx_openid)

        wx_userInfo = getUserInfo(access_token, wx_openid)
        nickname = wx_userInfo["nickname"]
        #nickname = unicode(nickname).encode('utf-8')
        logging.info("got nickname=[%r]", nickname)
        avatar = wx_userInfo['headimgurl']
        logging.info("got avatar=[%r]", avatar)

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

        url = API_DOMAIN + "/api/auth/wx/register"
        http_client = HTTPClient()
        random = str(uuid.uuid1()).replace('-', '')
        headers = {"Authorization":"Bearer "+random}
        _json = json_encode({'wx_openid':wx_openid,'nickname':nickname,'avatar':avatar})
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        session_ticket = data['rs']

        account_id = session_ticket['account_id']

        self.set_secure_cookie("access_token", session_ticket['access_token'])
        self.set_secure_cookie("expires_at", str(session_ticket['expires_at']))
        self.set_secure_cookie("account_id",account_id)
        # self.set_secure_cookie("wx_openid",wx_openid)

        timestamp = time.time()
        vendor_member = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, account_id)
        if not vendor_member:
            memeber_id = str(uuid.uuid1()).replace('-', '')
            _json = {'_id':memeber_id, 'vendor_id':vendor_id,
                'account_id':account_id, 'account_nickname':nickname, 'account_avatar':avatar,
                'comment':'...',
                'bonus':0, 'history_bonus':0, 'vouchers':0, 'crets':0,
                'rank':0, 'tour_leader':False,
                'distance':0,
                'create_time':timestamp, 'last_update_time':timestamp}
            vendor_member_dao.vendor_member_dao().create(_json)
            logging.info("create vendor member %r", account_id)
        else:
            _json = {'vendor_id':vendor_id,
                'account_id':account_id, 'account_nickname':nickname, 'account_avatar':avatar,
                'last_update_time':timestamp}
            vendor_member_dao.vendor_member_dao().update(_json)

        _voucher = voucher_pay_dao.voucher_pay_dao().query_not_safe(voucher_id);
        _voucher['amount'] = float(_voucher['amount']) / 100
        _voucher['price'] = float(_voucher['price']) / 100

        vendor_member = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, account_id)
        if(vendor_member):
            try:
                vendor_member['account_nickname']
            except:
                vendor_member['account_nickname'] = ''
            try:
                vendor_member['account_avatar']
            except:
                vendor_member['account_avatar'] = ''
        _avatar = vendor_member['account_avatar']
        _nickname = vendor_member['account_nickname']

        self.render('wx/voucher-order-confirm.html',
                vendor_id=vendor_id,
                voucher=_voucher)


class WxVoucherBuyStep2Handler(BaseHandler):
    def post(self):
        vendor_id = self.get_argument("vendor_id", "")
        logging.info("got vendor_id %r", vendor_id)
        voucher_id = self.get_argument("voucher_id", "")
        account_id = self.get_secure_cookie("account_id")

        _timestamp = time.time()
        # 一分钟内不能创建第二个订单,
        # 防止用户点击回退按钮，产生第二个订单
        _old_orders = voucher_order_dao.voucher_order_dao().query_by_account(voucher_id, account_id)
        # if len(_old_orders) > 0:
        #     for _old_order in _old_orders:
        #         if (_timestamp - _old_order['create_time']) < 60:
        #             return

        # # 订单申报数目
        # _applicant_num = self.get_argument("applicant_num", 1)
        # 转换成元
        _voucher = voucher_pay_dao.voucher_pay_dao().query_not_safe(voucher_id);
        _amount = _voucher['amount']
        _price = _voucher['price']
        _voucher_id = _voucher['_id']
        _create_time = _voucher['create_time']
        _expired_time = _voucher['expired_time']
        _qrcode_url = _voucher['qrcode_url']

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
        _status = ORDER_STATUS_BF_INIT
        if _price == 0:
            _status = ORDER_STATUS_WECHAT_PAY_SUCCESS
        _order_id = str(uuid.uuid1()).replace('-', '')
        _timestamp = time.time()

        # 创建订单索引
        order_index = {
            "_id": _order_id,
            "order_tyoe": "buy_voucher",
            "club_id": vendor_id,
            "item_type": "voucher",
            "item_id": _voucher_id,
            "item_name": _title,
            "distributor_type": "club",
            "distributor_id": guest_club_id,
            "create_time": _timestamp,
            "pay_type": "wxpay",
            "pay_status": _status,
            "total_amount": _amount, #已经转换为分，注意转为数值
        }
        self.create_order(order_index)

        _order = {"_id":_order_id, "vendor_id":vendor_id,
                "account_id":account_id, "account_avatar":_avatar, "account_nickname":_nickname,
                "voucher_id":_voucher_id, "voucher_price":_price, "voucher_amount":_amount,
                "pay_type":"wxpay","applicant_num":1,
                "create_time":_timestamp, "last_update_time":_timestamp,
                'status':_status, 'review':False} # status=99, 微信返回的支付状态
        voucher_order_dao.voucher_order_dao().create(_order);

        num = voucher_order_dao.voucher_order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "voucher_order":num})

        #创建微信订单
        _total_amount = int(_voucher['price'])
        _timestamp = (int)(time.time())
        if _total_amount != 0:
            # wechat 统一下单
            # _openid = self.get_secure_cookie("wx_openid")
            # logging.info("got _openid %r", _openid)
            # 从comm中统一取
            myinfo = self.get_myinfo_login()
            _openid = myinfo['login']

            _store_id = 'Aplan'
            logging.info("got _store_id %r", _store_id)
            _product_description = "voucher"
            logging.info("got _product_description %r", _product_description)

            wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
            wx_app_id = wx_app_info['wx_app_id']
            logging.info("got wx_app_id %r in uri", wx_app_id)
            wx_mch_key = wx_app_info['wx_mch_key']
            wx_mch_id = wx_app_info['wx_mch_id']
            wx_notify_domain = wx_app_info['wx_notify_domain']

            key = wx_mch_key
            nonceA = getNonceStr();
            logging.info("got nonceA %r", nonceA)
            #_ip = self.request.remote_ip
            _remote_ip = self.request.headers['X-Real-Ip']
            logging.info("got _remote_ip %r", _remote_ip)
            total_fee = str(_total_amount)
            logging.info("got total_fee %r", total_fee)
            notify_url = wx_notify_domain + '/bf/wx/voucher-orders/notify'
            logging.info("got notify_url %r", notify_url)
            signA = getOrderSign(_remote_ip, notify_url, wx_app_id, wx_mch_id, nonceA, _openid, key, _store_id, _order_id, _product_description, total_fee)
            logging.info("got signA %r", signA)

            _xml = '<xml>' \
                + '<appid>' + wx_app_id + '</appid>' \
                + '<attach>' + _store_id + '</attach>' \
                + '<body>' + _product_description + '</body>' \
                + '<mch_id>' + wx_mch_id + '</mch_id>' \
                + '<nonce_str>' + nonceA + '</nonce_str>' \
                + '<notify_url>' + notify_url + '</notify_url>' \
                + '<openid>' + _openid + '</openid>' \
                + '<out_trade_no>' + _order_id + '</out_trade_no>' \
                + '<spbill_create_ip>' + _remote_ip + '</spbill_create_ip>' \
                + '<total_fee>' + total_fee + '</total_fee>' \
                + '<trade_type>JSAPI</trade_type>' \
                + '<sign>' + signA + '</sign>' \
                + '</xml>'
            logging.info("got xml-------- %r", _xml)
            url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_xml)
            logging.info("got response %r", response.body)
            _order_return = parseWxOrderReturn(response.body)

            logging.info("got _timestamp %r", str(_timestamp))
            try:
                prepayId = _order_return['prepay_id']
            except:
                _order_return['prepay_id'] = ''
                prepayId = ''
            logging.info("got prepayId %r", prepayId)
            try:
                nonceB = _order_return['nonce_str']
            except:
                _order_return['nonce_str'] = ''
                nonceB = ''
            signB = getPaySign(_timestamp, wx_app_id, nonceB, prepayId, key)
            logging.info("got signB %r", signB)
            _order_return['pay_sign'] = signB
            _order_return['timestamp'] = _timestamp
            _order_return['app_id'] = wx_app_id
            _order_return['timestamp'] = _timestamp
            #_order_return['return_msg'] = 'OK'

            if(_order_return['return_msg'] == 'OK'):
                json = {'_id': _order_id, 'prepay_id': prepayId, 'status': ORDER_STATUS_WECHAT_UNIFIED_SUCCESS}
            else:
                json = {'_id': _order_id, 'prepay_id': prepayId, 'status': ORDER_STATUS_WECHAT_UNIFIED_FAILED}
            voucher_order_dao.voucher_order_dao().update(json)

        _voucher['amount'] = float(_voucher['amount']) / 100
        _voucher['price'] = float(_voucher['price']) / 100
        self.render('wx/voucher-pay-confirm.html',
                vendor_id=vendor_id,
                order_return=_order_return,
                voucher=_voucher,order=_order)


class WxVoucherBuyStep3Handler(tornado.web.RequestHandler):
    def get(self, vendor_id, voucher_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_id %r in uri", voucher_id)

        _account_id = self.get_secure_cookie("account_id")
        _order_id = self.get_argument("order_id", "")
        _voucher = voucher_pay_dao.voucher_pay_dao().query_not_safe(voucher_id)

        _timestamp = time.time()

        # 更新用户代金券
        _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _account_id)
        try:
            _customer_profile['vouchers']
        except:
            _customer_profile['vouchers'] = 0
        _vouchers_num = _customer_profile['vouchers'] + _voucher['amount']
        _timestamp = time.time()
        _json = {'vendor_id':vendor_id, 'account_id':_account_id, 'last_update_time':_timestamp,
                'vouchers':_vouchers_num}
        vendor_member_dao.vendor_member_dao().update(_json)

        # 每分配一个有偿代金券则生成一个普通代金券记录,方便个人中心查询
        _amount = _voucher['amount']
        _price = _voucher['price']
        _create_time = _voucher['create_time']
        _expired_time = _voucher['expired_time']
        _qrcode_url = _voucher['qrcode_url']

        json = {"_id":_order_id, "vendor_id":vendor_id, "qrcode_url":_qrcode_url,
                "create_time":_create_time, "last_update_time":_timestamp,
                "amount":_amount, "expired_time":_expired_time, "price":_price,
                'status':1, "account_id":_account_id} # status=1, 已分配，未使用
        voucher_dao.voucher_dao().create(json);


        self.render('wx/voucher-pay-success.html',
                vendor_id=vendor_id,
                voucher=_voucher)


# 线路市场首页
class WxTriprouterMarketHandler(tornado.web.RequestHandler):
    def get(self,vendor_id):

        # _array = trip_router_dao.trip_router_dao().query_by_open(vendor_id)
        triprouters_me = trip_router_dao.trip_router_dao().query_by_vendor(vendor_id)
        triprouters_share = triprouter_share_dao.triprouter_share_dao().query_by_vendor(vendor_id)

        # 处理一下自己线路
        for triprouter in triprouters_me:
            club = club_dao.club_dao().query(triprouter['vendor_id'])
            triprouter['club'] = club['club_name']
            triprouter['share'] = False

        _array = triprouters_me + triprouters_share

        self.render('wx/triprouter-index.html',
                vendor_id=vendor_id,
                triprouters=_array)

class WxTriprouterInfoHandler(tornado.web.RequestHandler):
    def get(self, vendor_id, triprouter_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got triprouter_id %r in uri", triprouter_id)

        _triprouter = trip_router_dao.trip_router_dao().query(triprouter_id)

        # 详细介绍 判断是否有article_id
        try:
            _triprouter['article_id']
        except:
            _triprouter['article_id']=''

        if(_triprouter['article_id']!=''):

            url = "http://"+STP+"/blogs/my-articles/" + _triprouter['article_id'] + "/paragraphs"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="GET")
            logging.info("got response %r", response.body)
            _paragraphs = json_decode(response.body)

            _triprouter_desc = ""
            for _paragraph in _paragraphs:
                if _paragraph["type"] == 'raw':
                    _triprouter_desc = _paragraph['content']
                    break
            _triprouter_desc = _triprouter_desc.replace('&', "").replace('mdash;', "").replace('<p>', "").replace("</p>"," ").replace("<section>","").replace("</section>"," ").replace("\n"," ")
            _triprouter['desc'] = _triprouter_desc + '...'

        else:
            _triprouter['desc'] = '...'


        # 相关活动
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        activitys = activity_dao.activity_dao().query_by_triprouter(triprouter_id)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            activity['end_time'] = timestamp_date(float(activity['end_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_app_id = wx_app_info['wx_app_id']
        logging.info("got wx_app_id %r in uri", wx_app_id)
        wx_app_secret = wx_app_info['wx_app_secret']
        wx_notify_domain = wx_app_info['wx_notify_domain']

        logging.info("------------------------------------uri: "+self.request.uri)
        _access_token = getAccessTokenByClientCredential(wx_app_id, wx_app_secret)
        _jsapi_ticket = getJsapiTicket(_access_token)
        _sign = Sign(_jsapi_ticket, wx_notify_domain+self.request.uri).sign()
        logging.info("------------------------------------nonceStr: "+_sign['nonceStr'])
        logging.info("------------------------------------jsapi_ticket: "+_sign['jsapi_ticket'])
        logging.info("------------------------------------timestamp: "+str(_sign['timestamp']))
        logging.info("------------------------------------url: "+_sign['url'])
        logging.info("------------------------------------signature: "+_sign['signature'])

        # _logined = False
        # wechat_open_id = self.get_secure_cookie("wechat_open_id")
        # if wechat_open_id:
        #     _logined = True

        _account_id = self.get_secure_cookie("account_id")

        self.render('wx/triprouter-info.html',
                vendor_id=vendor_id,
                triprouter=_triprouter,activitys=activitys,
                wx_app_id=wx_app_secret,
                wx_notify_domain=wx_notify_domain,
                sign=_sign, account_id=_account_id)
