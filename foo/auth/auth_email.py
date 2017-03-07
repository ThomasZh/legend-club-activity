#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 7x24hs.com
# thomas@7x24hs.com
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
import time
import sys
import os
import uuid
import smtplib
import hashlib
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
from bson import json_util
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import *
from tornado.httputil import url_concat
from bson import json_util

from comm import *
from global_const import *


class AuthEmailLoginHandler(BaseHandler):
    def get(self):
        logging.info(self.request)
        err_msg = ""
        self.render('auth/email-login.html', err_msg=err_msg)

    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        email = self.get_argument("lg_email", "")
        pwd = self.get_argument("lg_pwd", "")
        remember = self.get_argument("lg_remember", "")
        logging.info("try login as email:[%r] pwd:[%r] remember:[%r]", email, pwd, remember)

        # login
        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/api/auth/token"
            http_client = HTTPClient()
            data = {"code":code,
                    "login":email,
                    "pwd":pwd}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            session_ticket = json_decode(response.body)

            # is ops
            try:
                # 添加此帐号到俱乐部的普通用户帐号表中
                url = "http://api.7x24hs.com/api/clubs/"+CLUB_ID+"/signup"
                http_client = HTTPClient()
                _json = json_encode({"role":"user"})
                headers={"Authorization":"Bearer "+session_ticket['access_token']}
                response = http_client.fetch(url, method="POST", headers=headers, body=_json)
                logging.info("got response %r", response.body)

                # 校验是否为俱乐部管理员
                url = "http://api.7x24hs.com/api/clubs/"+CLUB_ID+"/myinfo-as-ops"
                http_client = HTTPClient()
                headers={"Authorization":"Bearer "+session_ticket['access_token']}
                response = http_client.fetch(url, method="GET", headers=headers)
                logging.info("got response %r", response.body)
            except:
                err_title = str( sys.exc_info()[0] );
                err_detail = str( sys.exc_info()[1] );
                logging.error("error: %r info: %r", err_title, err_detail)
                if err_detail == 'HTTP 404: Not Found':
                    err_msg = "您不是联盟的管理员!"
                    self.render('auth/phone-login.html', err_msg=err_msg)
                    return

            self.set_secure_cookie("access_token", session_ticket['access_token'])
            self.set_secure_cookie("expires_at", str(session_ticket['expires_at']))
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 404: Not Found':
                err_msg = "用户名或密码不正确!"
                self.render('auth/email-login.html', err_msg=err_msg)
                return

        self.redirect('/')


class AuthEmailRegisterHandler(BaseHandler):
    def get(self):
        err_msg = ""
        self.render('auth/email-register.html', err_msg=err_msg)

    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        email = self.get_argument("reg_email", "")
        pwd = self.get_argument("reg_pwd", "")
        logging.info("try register as email:[%r] pwd:[%r]", email, pwd)

        # register
        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/api/auth/accounts"
            http_client = HTTPClient()
            data = {"code":code,
                    "login":email,
                    "pwd":pwd}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            session_ticket = json_decode(response.body)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 409: Conflict':
                err_msg = "用户名已经注册!"
                self.render('auth/email-register.html', err_msg=err_msg)
                return

        err_msg = "注册成功，请登录!"
        self.render('auth/email-register.html', err_msg=err_msg)


class AuthEmailForgotPwdHandler(BaseHandler):
    def get(self):
        err_msg = "When you fill in your registered email address, you will be sent instructions on how to reset your password."
        self.render('auth/email-forgot-pwd.html', err_msg=err_msg)

    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        email = self.get_argument("fp_email", "")
        logging.info("try to send forgot password email to [%r]", email)

        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/api/auth/email/forgot-pwd"
            http_client = HTTPClient()
            data = {"code":code,
                    "email":email}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 404: Not Found':
                err_msg = "帐号不存在!"
                self.render('auth/forgot-pwd.html', err_msg=err_msg)
                return

        err_msg = "邮件已经发出, 请注意查收! 此邮件在5分钟内有效。"
        self.render('auth/email-forgot-pwd.html', err_msg=err_msg)


class AuthEmailResetPwdHandler(BaseHandler):
    def get(self):
        logging.info(self.request)
        ekey = self.get_argument("ekey", "")
        email = self.get_argument("email", "")
        logging.info("try reset email=[%r] password by ekey=[%r]", email, ekey)

        err_msg = ""
        self.render('auth/email-reset-pwd.html',
                err_msg=err_msg,
                email=email,
                ekey=ekey)

    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        email = self.get_argument("reset_email", "")
        ekey = self.get_argument("reset_ekey", "")
        pwd = self.get_argument("reset_pwd", "")
        logging.info("try to reset password email=[%r] ekey=[%r] pwd=[%r]", email, ekey, pwd)

        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/api/auth/email/reset-pwd"
            http_client = HTTPClient()
            data = {"code":code,
                    "email":email,
                    "ekey":ekey,
                    "pwd":pwd}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 404: Not Found':
                err_msg = "帐号不存在!"
                self.render('auth/email-reset-pwd.html',
                        err_msg=err_msg,
                        email=email,
                        ekey=ekey)
                return
            elif err_detail == 'HTTP 408: Request Timeout':
                err_msg = "请求超时, 在5分钟内有效!"
                self.render('auth/email-reset-pwd.html',
                        err_msg=err_msg,
                        email=email,
                        ekey=ekey)
                return

        err_msg = "密码修改成功, 请重新登录!"
        self.render('auth/email-reset-pwd.html',
                err_msg=err_msg,
                email=email,
                ekey=ekey)


class AuthWelcomeHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        self.render('auth/welcome.html')


class AuthLogoutHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        access_token = self.get_secure_cookie("access_token")

        # logout
        url = "http://api.7x24hs.com/api/auth/tokens"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="DELETE", headers={"Authorization":"Bearer "+access_token})
        logging.info("got response %r", response.body)
        self.clear_cookie("access_token")
        self.clear_cookie("expires_at")
        self.clear_cookie("login_next")
        self.clear_cookie("refresh_token")

        self.redirect("/");
