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
