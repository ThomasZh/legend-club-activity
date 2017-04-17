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


import tornado.web
import logging
import time
import sys
from global_const import *
from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat
import html2text
import markdown
import re


class WxMpVerifyHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('rZAV6WH7J2WhqAIs')
        return


class WxMpVerify2Handler(tornado.web.RequestHandler):
    def get(self):
        self.finish('UwBwsF7uHi57Xd6e')
        return


class singleton(object):
    _singleton = None;
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = object.__new__(cls);
        return cls._singleton;


class PageNotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('comm/page_404.html')


def timestamp_friendly_date(value):
    #_format = '%Y-%m-%d %H:%M:%S'
    y_format = '%Y'
    m_format = '%m'
    d_format = '%d'
    w_format = '%w'
    # value is timestamp(int), eg: 1332888820
    _value = time.localtime(value)
    _current = time.localtime()
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    current_y_dt = time.strftime(y_format, _current)
    y_dt = time.strftime(y_format, _value)
    m_dt = time.strftime(m_format, _value)
    d_dt = time.strftime(d_format, _value)
    w_dt = time.strftime(w_format, _value)
    if w_dt == '0':
        if current_y_dt == y_dt:
            _dt = str(int(m_dt)) + '月' + str(int(d_dt)) + ' 星期日'
        else:
            _dt = str(int(y_dt)) + '年' + str(int(m_dt)) + '月' + str(int(d_dt)) + ' 星期日'
    else:
        if current_y_dt == y_dt:
            _dt = str(int(m_dt)) + '月' + str(int(d_dt)) + ' 星期' + w_dt
        else:
            _dt = str(int(y_dt)) + '年' + str(int(m_dt)) + '月' + str(int(d_dt)) + ' 星期' + w_dt
    return _dt


def timestamp_date(value):
    #_format = '%Y-%m-%d %H:%M:%S'
    _format = '%m/%d/%Y'
    # value is timestamp(int), eg: 1332888820
    _value = time.localtime(value)
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    _dt = time.strftime(_format, _value)
    return _dt


def date_timestamp(dt):
     # dt is string
     time.strptime(dt, '%m/%d/%Y')
     ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=-1)
     # "2012-03-28 06:53:40" to timestamp(int)
     _timestamp = time.mktime(time.strptime(dt, '%m/%d/%Y'))
     return int(_timestamp)


def timestamp_datetime(value):
    #_format = '%Y-%m-%d %H:%M:%S'
    _format = '%Y-%m-%d %H:%M'
    # value is timestamp(int), eg: 1332888820
    _value = time.localtime(value)
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    _dt = time.strftime(_format, _value)
    return _dt


def datetime_timestamp(dt):
     # dt is string
     time.strptime(dt, '%Y-%m-%d %H:%M')
     ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=-1)
     # "2012-03-28 06:53:40" to timestamp(int)
     _timestamp = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M'))
     return int(_timestamp)


def time_span(ts):
    delta = datetime.now() - ts
    if delta.days >= 365:
        return '%d年前' % (delta.days / 365)
    elif delta.days >= 30:
        return '%d个月前' % (delta.days / 30)
    elif delta.days > 0:
        return '%d天前' % delta.days
    elif delta.seconds < 60:
        return "%d秒前" % delta.seconds
    elif delta.seconds < 60 * 60:
        return "%d分钟前" % (delta.seconds / 60)
    else:
        return "%d小时前" % (delta.seconds / 60 / 60)


class BaseHandler(tornado.web.RequestHandler):

    def points_decrease(self, club_id, account_id, num):
        headers = {"Authorization":"Bearer "+DEFAULT_USER_ID}

        _json = json_encode({"points":num, "action":"decrease"})

        url = API_DOMAIN + "/api/clubs/" + club_id + "/users/" + account_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got points_decrease response.body=[%r]", response.body)


    def points_increase(self, club_id, account_id, num):
        headers = {"Authorization":"Bearer "+DEFAULT_USER_ID}

        _json = json_encode({"points":num, "action":"increase"})

        url = API_DOMAIN + "/api/clubs/" + club_id + "/users/" + account_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got points_increase response.body=[%r]", response.body)


    def get_club_user(self, club_id, account_id):
        headers = {"Authorization":"Bearer "+DEFAULT_USER_ID}

        url = API_DOMAIN + "/api/clubs/" + club_id + "/users/" + account_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got club_user response.body=[%r]", response.body)
        data = json_decode(response.body)
        if data['err_code'] == 404:
            return None
        return data['rs']


    def create_club_user(self, club_id, account_id):
        headers = {"Authorization":"Bearer "+DEFAULT_USER_ID}

        url = API_DOMAIN + "/api/clubs/" + club_id + "/users/" + account_id
        http_client = HTTPClient()
        _json = json_encode(headers)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("create club_user response.body=[%r]", response.body)


    def get_order_index(self, order_id):
        headers = {"Authorization":"Bearer "+DEFAULT_USER_ID}

        url = API_DOMAIN + "/api/orders/" + order_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got order_index response.body=[%r]", response.body)
        data = json_decode(response.body)
        if data['err_code'] == 404:
            return None
        return data['rs']


    def update_order_unified(self, order_unified):
        headers = {"Authorization":"Bearer "+DEFAULT_USER_ID}

        url = API_DOMAIN + "/api/orders/" + order_unified['_id'] + "/unified"
        http_client = HTTPClient()
        _json = json_encode(order_unified)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)


    def update_order_payed(self, order_payed):
        headers = {"Authorization":"Bearer "+DEFAULT_USER_ID}

        url = API_DOMAIN + "/api/orders/" + order_payed['_id'] + "/payed"
        http_client = HTTPClient()
        _json = json_encode(order_payed)
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got response.body %r", response.body)


    def get_symbol_object(self, _id):
        url = API_DOMAIN + "/api/symbols/" + _id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got symbol_object=[%r]", response.body)
        data = json_decode(response.body)
        if data['err_code'] == 404:
            return None
        symbol_object = data['rs']
        return symbol_object


    def create_symbol_object(self, symbol_object):
        url = API_DOMAIN + "/api/symbols"
        _json = json_encode(symbol_object)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("create symbol_object=[%r]", response.body)
        data = json_decode(response.body)
        if data['err_code'] == 404:
            return None
        symbol_object = data['rs']
        return symbol_object['_id']


    def update_symbol_object(self, symbol_object):
        url = API_DOMAIN + "/api/symbols/" + symbol_object['_id']
        _json = json_encode(symbol_object)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="PUT", body=_json)
        logging.info("create symbol_object=[%r]", response.body)


    def get_counter(self, item_id):
        url = API_DOMAIN + "/api/counters/" + item_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got get_counter %r", response.body)
        data = json_decode(response.body)
        if data['err_code'] == 404:
            return None
        counter = data['rs']
        return counter


    def counter_increase(self, item_id, parameter):
        url = API_DOMAIN + "/api/counters/" + item_id + "/parameters/" + parameter +"/increase"
        http_client = HTTPClient()
        data = {"appid":"7x24hs:activity",
                "app_secret":"2518e11b3bc89ebec594350d5739f29e"}
        _json = json_encode(data)
        response = http_client.fetch(url, method="PUT", body=_json)
        logging.info("got counter_increase %r", response.body)
        data = json_decode(response.body)
        counter = data['rs']
        num = counter['num']
        return num


    def counter_decrease(self, item_id, parameter):
        url = API_DOMAIN + "/api/counters/" + item_id + "/parameters/" + parameter +"/decrease"
        http_client = HTTPClient()
        data = {"appid":"7x24hs:activity",
                "app_secret":"2518e11b3bc89ebec594350d5739f29e"}
        _json = json_encode(data)
        response = http_client.fetch(url, method="PUT", body=_json)
        logging.info("got counter_increase %r", response.body)
        data = json_decode(response.body)
        counter = data['rs']
        num = counter['num']
        return num


    def get_user_basic_info(self, account_id):
        params = {"filter":"basic", "by":"account_id"}
        url = url_concat(API_DOMAIN + "/api/profiles/" + account_id, params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        data = json_decode(response.body)
        account = data['rs']
        return account


    def get_club_basic_info(self, club_id):
        params = {"filter":"basic"}
        url = url_concat(API_DOMAIN + "/api/clubs/" + club_id, params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        data = json_decode(response.body)
        club = data['rs']
        return club


    def get_article(self, article_id):
        url = API_DOMAIN + "/api/articles/" + article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got article response %r", response.body)
        data = json_decode(response.body)
        if data['err_code'] == 404:
            return None

        article = data['rs']
        html = article['paragraphs']
        # 为图片延迟加载准备数据
        # < img alt="" src="http://bighorn.b0.upaiyun.com/blog/2016/11/2/758f7478-d406-4f2e-9566-306a963fb979" />
        # < img data-original="真实图片" src="占位符图片">
        ptn="(<img src=\"http[s]*://[\w\.\/\-]+\" />)"
        img_ptn = re.compile(ptn)
        imgs = img_ptn.findall(html)
        for img in imgs:
            logging.info("got img %r", img)
            ptn="<img src=\"(http[s]*://[\w\.\/\-]+)\" />"
            url_ptn = re.compile(ptn)
            urls = url_ptn.findall(html)
            url = urls[0]
            logging.info("got url %r", url)
            #html = html.replace(img, "< img class=\"lazy\" data-original=\""+url+"\" src=\"/static/images/weui.png\" width=\"100%\" height=\"480\" />")
            html = html.replace(img, "<img width='100%' src='"+url+"' />")
        article['paragraphs'] = html
        return article


    def get_code(self):
        url = API_DOMAIN + "/api/auth/codes"
        http_client = HTTPClient()
        data = {"appid":"7x24hs:blog",
                "app_secret":"2518e11b3bc89ebec594350d5739f29e"}
        _json = json_encode(data)
        response = http_client.fetch(url, method="POST", body=_json)
        data = json_decode(response.body)
        session_code = data['rs']
        logging.info("got session_code %r", session_code)
        code = session_code['code']
        return code


    def get_myinfo_login(self):
        access_token = self.get_secure_cookie("access_token")

        url = API_DOMAIN +"/api/myinfo?filter=login"
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        data = json_decode(response.body)
        myinfo = data['rs']
        logging.info("got myinfo %r", myinfo)
        # myinfo['login']: wx_openid
        return myinfo


    def write_error(self, status_code, **kwargs):
        host = self.request.headers['Host']
        logging.info("got host %r", host)

        try:
            reason = ""
            for line in traceback.format_exception(*kwargs["exc_info"]):
                if "HTTP 404: Not Found" in line:
                    self.render('comm/page-404.html')
                    self.finish()
                reason += line
            logging.info("got status_code %r reason %r", status_code, reason)

            params = {"app":"club-ops", "sys":host, "level":status_code, "message": reason}
            url = url_concat("http://kit.7x24hs.com/api/sys-error", params)
            http_client = HTTPClient()
            _json = json_encode(params)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response.body %r", response.body)
        except:
            logging.warn("write log to http://kit.7x24hs.com/api/sys-error error")

        self.render("comm/page-500.html",
                status_code=status_code)


class AuthorizationHandler(BaseHandler):

    def create_apply(self, apply_index):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}

        url = API_DOMAIN + "/api/applies"
        http_client = HTTPClient()
        _json = json_encode(apply_index)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        return rs['_id']


    def create_order(self, order_index):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}

        url = API_DOMAIN + "/api/orders"
        http_client = HTTPClient()
        _json = json_encode(order_index)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)


    def check_apply(self, apply_id):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}

        url = API_DOMAIN + "/api/applies/" + apply_id + "/check"
        http_client = HTTPClient()
        _json = json_encode(headers)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)


    def check_order(self, order_id):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}

        url = API_DOMAIN + "/api/orders/" + order_id + "/check"
        http_client = HTTPClient()
        _json = json_encode(headers)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)


    def publish_article(self, article_id):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}

        url = API_DOMAIN + "/api/articles/" + article_id + "/publish"
        http_client = HTTPClient()
        _json = json_encode(headers)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)


    def unpublish_article(self, article_id):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}

        url = API_DOMAIN + "/api/articles/" + article_id + "/unpublish"
        http_client = HTTPClient()
        _json = json_encode(headers)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)


    def update_article_categories(self, article_id, ids):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode(ids)

        url = API_DOMAIN + "/api/articles/" + article_id + "/categories"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)


    def update_article(self, article):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode(article)

        url = API_DOMAIN + "/api/articles/" + article['_id']
        http_client = HTTPClient()
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got response %r", response.body)


    def create_article(self, article):
        access_token = self.get_access_token()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode(article)

        url = API_DOMAIN + "/api/articles"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("create article response %r", response.body)


    def get_access_token(self):
        access_token = self.get_secure_cookie("access_token")
        if access_token:
            logging.info("got access_token=[%r] from cookie", access_token)
        else:
            try:
                access_token = self.request.headers['Authorization']
                access_token = access_token.replace('Bearer ','')
            except:
                logging.warn("got access_token=[null] from headers")
                self.set_status(401) # Unauthorized
                self.write('Unauthorized')
                self.finish()
                return
            logging.info("got access_token=[%r] from headers", access_token)
        return access_token


    def get_ops_info(self):
        access_token = self.get_secure_cookie("access_token")

        try:
            params = {"filter":"ops"}
            url = url_concat(API_DOMAIN+"/api/myinfo", params)
            http_client = HTTPClient()
            headers={"Authorization":"Bearer "+access_token}
            response = http_client.fetch(url, method="GET", headers=headers)
            logging.info("got response %r", response.body)
            # account_id,nickname,avatar,club_id,club_name,league_id,_rank
            data = json_decode(response.body)
            ops = data['rs']
            return ops
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 404: Not Found':
                err_msg = "您不是俱乐部的管理员!"
                self.redirect("/ops/auth/phone/login")
                return
            else:
                err_msg = "系统故障, 请稍后尝试!"
                self.redirect("/ops/auth/phone/login")
                return


    def get_current_user(self):
        self.set_secure_cookie("login_next", self.request.uri)

        access_token = self.get_secure_cookie("access_token")
        logging.info("got access_token %r from cookie", access_token)
        if not access_token:
            return None
        else:
            expires_at = self.get_secure_cookie("expires_at")
            logging.info("got expires_at %r from cookie", expires_at)
            if not expires_at:
                return None
            else:
                _timestamp = int(time.time())
                if int(expires_at) > _timestamp:
                    return access_token
                else:
                    # Logic: refresh_token
                    refresh_token = self.get_secure_cookie("refresh_token")
                    if not refresh_token:
                        return None
                    else:
                        try:
                            url = API_DOMAIN+"/api/auth/tokens"
                            http_client = HTTPClient()
                            headers={"Authorization":"Bearer "+refresh_token}
                            data = {"action":"refresh"}
                            _json = json_encode(data)
                            logging.info("request %r body %r", url, _json)
                            response = http_client.fetch(url, method="POST", headers=headers, body=_json)
                            logging.info("got response %r", response.body)
                            data = json_decode(response.body)
                            session_ticket = data['rs']
                            self.set_secure_cookie("access_token", session_ticket['access_token'])
                            self.set_secure_cookie("expires_at", str(session_ticket['expires_at']))
                            self.set_secure_cookie("refresh_token", session_ticket['refresh_token'])
                            return session_ticket['access_token']
                        except:
                            return None
                    return None

def markdown_html(markdown_content):
    html = markdown.markdown(markdown_content)
    html = html.replace('\n','')
    logging.info("got html of content %r", html)

    # 图片Markdown格式->html格式
    # ![](https://tripc2c-club-title.b0.upaiyun.com/articles/bg/2017/2/28/becf7582-3c0c-4305-9440-2fe088d516ee.jpeg)
    # <img alt="" src="http://bighorn.b0.upaiyun.com/blog/2016/11/2/758f7478-d406-4f2e-9566-306a963fb979" />
    markdown_img_ptn = "(!\[[\w\.\/\-]*\]\(http[s]*://[\w\.\/\-]+\))"
    img_ptn = re.compile(markdown_img_ptn)
    markdown_imgs = img_ptn.findall(html)
    for markdown_img in markdown_imgs:
        logging.info("got html ![](img_url) of content %r", markdown_img)
        ptn="(http[s]*://[\w\.\/\-]+)"
        url_ptn = re.compile(ptn)
        urls = url_ptn.findall(markdown_img)
        url = urls[0]
        logging.info("got url %r", url)
        html = html.replace(markdown_img, "<img src=\""+url+"\" />")

    return html


def html_markdown(html):
    # 使用 html2text 将网页内容转换为 Markdown 格式
    h = html2text.HTML2Text()
    h.ignore_links = False
    markdown_content = h.handle(html)
    logging.info("got markdown content %r", markdown_content)
    return markdown_content
