#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 planc2c.com
# thomas@time2box.com
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


import base64
from gettext import gettext as _
import logging
import uuid

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient

from comm import BaseHandler
from global_const import STP


class LoginHandler(BaseHandler):
    def get(self):
        _ = self.locale.translate
        _login_name = self.get_secure_cookie("login_name")
        if _login_name == None:
            _login_name = ""
        _remember_me = self.get_secure_cookie("remember_me")
        if _remember_me == None:
            _remember_me = "off"
        #print "login_name: "+_login_name
        #print "remember_me: " + _remember_me
        self.render('auth/login.html', err_msg="", login_name=_login_name, remember_me=_remember_me)

    def post(self):
        _login_name = self.get_argument("input-email")
        logging.info("got _login_name %r", _login_name)
        _md5pwd = self.get_argument("input-password")
        _remember_me = self.get_argument("remember-me", "off")
        _user_agent = self.request.headers["User-Agent"]
        _user_locale = self.request.headers["Accept-Language"]
        _device_id = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        logging.info("got _remember_me %r", _remember_me)
        logging.info("got _user_agent %r", _user_agent)
        logging.info("got _user_locale %r", _user_locale)
        logging.info("got _device_id %r", _device_id)

        try:
            params = { "osVersion" : "webkit:"+_user_agent,
                  "gateToken" : "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
                  "deviceId" : _device_id,
                  "password" : _md5pwd,
                  "email" : _login_name}
            _json = json_encode(params)
            url = "http://"+STP+"/vendor/login"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            #print response.body
            logging.info("got response.body %r", response.body)
            _stp_session = json_decode(response.body)
            _session_ticket = _stp_session["sessionToken"]
            account_id = _stp_session["accountId"]

            self.set_secure_cookie("session_ticket", _session_ticket)
            self.set_secure_cookie("login_name", _login_name)
            self.set_secure_cookie("remember_me", _remember_me)
            self.set_secure_cookie("account_id", account_id)
            self.redirect("/")
        except Exception:
            _err_msg = _("Please enter a correct username and password.")
            self.render('auth/login.html', err_msg=_err_msg,
                        login_name=_login_name, remember_me=_remember_me)


class LogoutHandler(BaseHandler):
    def get(self):
        _remember_me = self.get_secure_cookie("remember_me")
        if _remember_me == None:
            _remember_me = "off"
        #print  _remember_me

        if _remember_me == "off":
            self.clear_cookie("session_ticket")
            self.clear_cookie("login_name")
            self.clear_cookie("remember_me")
        else:
            self.clear_cookie("session_ticket")
        self.redirect("/")


# regitser by mobile phone
class RegisterHandler(BaseHandler):
    def post(self):
        loginname = self.get_argument("register-loginname")
        nickname = self.get_argument("register-nickname")
        md5pwd = self.get_argument("register-password")
        logging.info("got loginname %r", loginname)
        logging.info("got nickname %r", nickname)

        try:
            params = { "loginType": 1602,
                  "md5pwd": md5pwd,
                  "nickname": nickname,
                  "loginName": loginname}
            _json = json_encode(params)

            url = "http://"+STP+"/account/register"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)

            self.set_secure_cookie("login_name", loginname)
            self.redirect("/auth/login")
        except Exception:
            _err_msg = _("Loginname already exist, please try another.")
            self.render('auth/login.html', login_name="", remember_me="off", err_msg=_err_msg)


class ForgotPwdHandler(BaseHandler):
    def get(self):
        _ = self.locale.translate
        login_name = self.get_secure_cookie("login_name")
        if login_name == None:
            login_name = ""
        self.render('auth/forgot-pwd.html', err_msg='', login_name=login_name, remember_me='off')

    def post(self):
        loginname = self.get_argument("forgotpwd-loginname", "")
        #device_id = str(uuid.uuid1()).replace('-', '')
        #device_id = "6d2fb330516911e6a84fa45e60efbf2d"
        verification_code = self.get_argument("forgotpwd-verification-code")
        md5pwd = self.get_argument("forgotpwd-password")

        params = {"phone":loginname, "ekey":verification_code, "newPassword":md5pwd, "deviceId":loginname}
        _json = json_encode(params)
        logging.info("got params %r", _json)
        url = "http://"+STP+"/account/reset-phone-password"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got response %r", response.body)

        _err_msg = _("Email has been send to your mail, please check it.")
        self.render('auth/login.html', err_msg=_err_msg,
                    login_name=loginname, remember_me="off")


class AuthApiGetVerificationCodeHandler(BaseHandler):
    def get(self):
        phone = self.get_argument("loginname", "")
        #device_id = str(uuid.uuid1()).replace('-', '')
        #device_id = "6d2fb330516911e6a84fa45e60efbf2d"

        params = {"verificationType":1802, "phone":phone, "deviceId":phone}
        _json = json_encode(params)
        logging.info("got params %r", _json)
        url = "http://"+STP+"/account/apply-for-binding-phone"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got response %r", response.body)

        self.finish("ok")


class ResetPwdHandler(BaseHandler):
    def get(self):
        _ = self.locale.translate
        _ekey = self.get_argument("ekey", "")
        self.render('account/reset-pwd.html', ekey=_ekey)

    def post(self):
        _ekey = self.get_argument("ekey", "")
        _md5pwd = self.get_argument("input-password", "")
        #print _ekey

        params = {"ekey" : _ekey}
        _json = json_encode(params)
        url = "http://"+STP+"/account/verify-email"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", body=_json)
        #print response.body
        _ekey_object = json_decode(response.body)
        _email = _ekey_object["email"]

        params = {"ekey" : _ekey, "email": _email, "newPassword": _md5pwd}
        _json = json_encode(params)
        url = "http://"+STP+"/account/reset-password"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", body=_json)
        #print response.body

        _err_msg = _("Password has been changed, please sign in.")
        self.render('auth/login.html', err_msg=_err_msg,
                    login_name="", remember_me="off")


def ssoLogin(loginType, loginName, nickname, avatarUrl, userAgent, lang):
    _device_id = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
    params = {"gateToken" : "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            "deviceId": _device_id, "osVersion":"webkit:"+userAgent,
            "loginType": loginType,
            "loginName": loginName, "nickname": nickname, "imageUrl" : avatarUrl, "lang" : lang}
    _json = json_encode(params)
    url = "http://"+STP+"/account/ssologin"
    http_client = HTTPClient()
    response = http_client.fetch(url, method="POST", body=_json)
    logging.info("got response %r", response.body)
    stpSession = json_decode(response.body)
    return stpSession
