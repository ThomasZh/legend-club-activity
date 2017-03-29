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

def get_club_info(access_token,club_id):
    try:
        headers={"Authorization":"Bearer "+access_token}
        url = API_DOMAIN+"/api/clubs/"+club_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET", headers=headers)
        data = json_decode(response.body)
        err_code = data['err_code']
        if err_code == 200:
            club = data['rs']
        else:
            club =  None
        logging.info("got club info>>>>>>>>>>> %r",club)
        return club
    except:
        return
