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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat

from comm import BaseHandler
from comm import timestamp_datetime
from comm import datetime_timestamp
from comm import timestamp_date
from comm import date_timestamp

from global_const import VENDOR_ID
from global_const import STP


class VendorRegisterStep1Handler(tornado.web.RequestHandler):
    def get(self):
        self.render('alliance/vendor-register-step1.html', err_msg="")

    def post(self):
        phone = self.get_argument("phone", "")
        vcode = self.get_argument("vcode", "")  # verification code
        logging.info("got phone %r from args", phone)
        logging.info("got vcode %r from args", vcode)

        # account is exist?
        try:
            md5pwd = hashlib.md5("vcode").hexdigest();
            params = { "loginType": 1602,
                  "md5pwd": md5pwd,
                  "nickname": phone,
                  "loginName": phone}
            _json = json_encode(params)

            url = "http://"+STP+"/account/register"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)

            self.set_secure_cookie("login_name", phone)

            # vendor is exist?
            self.render('alliance/vendor-register-step2.html')
        except:
            # phone already exist

            params = { "verificationType": 1802,
                    "deviceId": phone,
                    "phone": phone,
                    "verificationCode": vcode}
            _json = json_encode(params)

            try:
                url = "http://"+STP+"/account/verify-phone-vcode-pair"
                http_client = HTTPClient()
                response = http_client.fetch(url, method="POST", body=_json)
                logging.info("got response %r", response.body)
            except:
                # fail, return "phone & vcode not pair" message
                err_msg = "phone & vcode not pair"
                self.render('alliance/vendor-register-step1.html', err_msg=err_msg)
            else:
                # get my accountId
                url = "http://"+STP+"/accounts/search/tel/"+phone
                http_client = HTTPClient()
                response = http_client.fetch(url, method="GET")
                logging.info("got response %r", response.body)
                account = json_decode(response.body)
                account_id = account['accountId']

                self.set_secure_cookie("account_id", account_id)

                # vendor is exist?
                params = {"ranks":1, "offset":0, "limit":10}
                url = url_concat("http://"+STP+"/clubs/someone/"+account_id, params)
                http_client = HTTPClient()
                response = http_client.fetch(url, method="GET")
                logging.info("got response %r", response.body)
                clubs = json_decode(response.body)

                logging.info("got clubs %r", len(clubs))
                if len(clubs) == 0:
                    self.render('alliance/vendor-register-step2.html')
                else:
                    club = None
                    for data in clubs:
                        club = data
                        break
                    club_id = club['id']
                    logging.info("got club_id %r", club_id)

                    try:
                        params = {"fields":"name,regulations,introduction,bgImageUrls,avatarUrl"}
                        url = url_concat("http://"+STP+"/clubs/"+club['id'], params)
                        http_client = HTTPClient()
                        response = http_client.fetch(url, method="GET")
                        logging.info("got response %r", response.body)
                        club = json_decode(response.body)

                        try:
                            club['avatarUrl']
                        except:
                            club['avatarUrl'] = ""
                        logging.debug("got avatarUrl %r", club['avatarUrl'])
                    except:
                        logging.error("got club %r error", club_id)

                    self.render('alliance/vendor-register-step3.html', club=club)


class VendorRegisterStep2Handler(tornado.web.RequestHandler):
    def post(self):
        account_id = self.get_secure_cookie("account_id")

        name = self.get_argument("name", "")
        regulations = self.get_argument("regulations", "")
        introduction = self.get_argument("introduction", "")
        avatar_img_url = self.get_argument("avatar_img_url", "")
        bk_img_urls = self.get_arguments("bk_img_urls")
        logging.info("got name %r", name)
        logging.info("got regulations %r", regulations)
        logging.info("got introduction %r", introduction)
        logging.info("got avatar_img_url %r", avatar_img_url)
        logging.info("got bk_img_urls %r", bk_img_urls)

        params = {"name":name,
                "regulations":regulations,
                "introduction":introduction,
                "avatarUrl":avatar_img_url,
                "bgImageUrls":bk_img_urls}
        _json = json_encode(params)

        url = "http://"+STP+"/clubs/create/"+account_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got response %r", response.body)
        rs = json_decode(response.body)
        club_id = rs['clubId']
        logging.info("got club_id %r", club_id)

        params = {"fields":"name,regulations,introduction,bgImageUrls,avatarUrl"}
        url = url_concat("http://"+STP+"/clubs/"+club_id, params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        club = json_decode(response.body)

        try:
            club['avatarUrl']
        except:
            club['avatarUrl'] = ""

        self.render('alliance/vendor-register-step3.html', club=club)
