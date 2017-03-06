#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 Time2Box
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

import json
from bson import json_util
import logging
import random
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat
import tornado.web

from comm import BaseHandler
from comm import timestamp_datetime
from comm import datetime_timestamp
from comm import timestamp_date
from comm import date_timestamp

from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao

from global_const import STP


# -------- ajax request handler -------------

# 提供给前端的无会话响应
# @2016/05/28
class MyArticleXHRHandler(tornado.web.RequestHandler):
    def get(self):
        _article_id = (self.request.arguments['id'])[0]

        url = "http://"+STP+"/blogs/my-articles/" + _article_id + "/paragraphs"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")

        self.write(response.body)
        self.finish()

# -------- ajax handler complete ------------

class MyArticlesHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        _timestamp = long(time.time() * 1000)
        params = {"before": _timestamp, "limit": 20}
        url = url_concat("http://"+STP+"/blogs/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _articles = json_decode(response.body)

        for _article in _articles:
            _timestamp = _article["timestamp"]
            _datetime = timestamp_datetime(_timestamp / 1000)
            _article["timestamp"] = _datetime

        self.render('blog/my-articles.html', articles=_articles)


class MyArticleHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        _article_id = (self.request.arguments['id'])[0]
        logging.info("article_id: ", _article_id)

        url = "http://"+STP+"/blogs/articles/" + _article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _article = json_decode(response.body)
        _timestamp = _article["timestamp"]
        _datetime = timestamp_datetime(_timestamp / 1000)
        _article["timestamp"] = _datetime

        url = "http://"+STP+"/blogs/my-articles/" + _article_id + "/paragraphs"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _paragraphs = json_decode(response.body)

        self.render('blog/my-article.html', article=_article, paragraphs=_paragraphs, scrollToParagraphId="")

class AddArticleHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        self.render('blog/add-article.html')

    def post(self):
        _ticket = self.get_secure_cookie("session_ticket")
        _title = (self.request.arguments['title'])[0]
        _content = (self.request.arguments['content'])[0]
        _img_url = (self.request.arguments['imgUrl'])[0]
        logging.info("got title %r", _title)
        logging.info("got title %r", _content)
        logging.info("got title %r", _img_url)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/articles", params)
            data = {"title": _title, "content": _content, "imgUrl": _img_url}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)

            _timestamp = long(time.time() * 1000)
            params = {"before": _timestamp, "limit": 20}
            url = url_concat("http://"+STP+"/blogs/articles", params)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="GET")
            logging.info("got response %r", response.body)
            _articles = json_decode(response.body)

            for _article in _articles:
                _timestamp = _article["timestamp"]
                _datetime = timestamp_datetime(_timestamp / 1000)
                _article["timestamp"] = _datetime

            self.render('blog/my-articles.html', articles=_articles)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class AddParagraphHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        #用type区分
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = (self.request.arguments['article_id'])[0]
        logging.info("article_id %r ", _article_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/add-paragraph.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,
                travel_type=_travel_type,
                article_id=_article_id)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        #用于区分是活动还是线路
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = (self.request.arguments['article_id'])[0]
        _type = (self.request.arguments['type'])[0]
        _content = (self.request.arguments['content'])[0]
        logging.info("got travel_type %r", _travel_type)
        logging.info("got type %r", _type)
        logging.info("got content %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs", params)
            data = {"articleId": _article_id, "type": _type, "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            _paragraph_id = json_decode(response.body)

            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class AddParagraphAfterHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _brother_id = self.get_argument("brother_id", "")
        logging.info("article_id: ", _article_id)
        logging.info("brother_id: ", _brother_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/add-paragraph-after.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,
                travel_type=_travel_type,
                article_id=_article_id,
                 brother_id=_brother_id)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _brother_id = self.get_argument("brother_id", "")
        _type = (self.request.arguments['type'])[0]
        _content = (self.request.arguments['content'])[0]
        logging.info("article_id: ", _article_id)
        logging.info("brother_id: ", _brother_id)
        logging.info("got type %r", _type)
        logging.info("got content %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_brother_id+"/after", params)
            data = {"articleId": _article_id, "type": _type, "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            _paragraph_id = json_decode(response.body)
            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class AddParagraphRawHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        logging.info("article_id: ", _article_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/add-paragraph-raw.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,
                travel_type=_travel_type,
                article_id=_article_id)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        #用于区分是活动还是线路
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _content = self.get_argument("content", "")
        logging.info("got article_id %r", _article_id)
        logging.info("got content %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs", params)
            data = {"articleId": _article_id, "type": "raw", "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            _paragraph_id = json_decode(response.body)
            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class AddParagraphRawAfterHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        #用于区分是活动还是线路
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _brother_id = self.get_argument("brother_id", "")
        logging.info("article_id: ", _article_id)
        logging.info("brother_id: ", _brother_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/add-paragraph-raw-after.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id, travel_type=_travel_type,
                article_id=_article_id, brother_id=_brother_id)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _brother_id = self.get_argument("brother_id", "")
        _content = (self.request.arguments['content'])[0]
        logging.info("article_id: ", _article_id)
        logging.info("brother_id: ", _brother_id)
        logging.info("got content %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_brother_id+"/after", params)
            data = {"articleId": _article_id, "type": "raw", "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            _paragraph_id = json_decode(response.body)

            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class AddParagraphImgHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        #用于区分是活动还是线路
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        logging.info("article_id: ", _article_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/add-paragraph-img.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,
                travel_type=_travel_type,
                article_id=_article_id)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _content = self.get_argument("content", "")
        logging.info("got article_id %r", _article_id)
        logging.info("got img %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs", params)
            data = {"articleId": _article_id, "type": "img", "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            _paragraph_id = json_decode(response.body)

            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class AddParagraphImgAfterHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _brother_id = self.get_argument("brother_id", "")
        logging.info("article_id: ", _article_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/add-paragraph-img-after.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,travel_type=_travel_type,
                article_id=_article_id, brother_id=_brother_id)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _brother_id = self.get_argument("brother_id", "")
        _content = (self.request.arguments['content'])[0]
        logging.info("got article_id %r", _article_id)
        logging.info("got img %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_brother_id+"/after", params)
            data = {"articleId": _article_id, "type": "img", "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            _paragraph_id = json_decode(response.body)

            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class EditParagraphHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _paragraph_id = self.get_argument("id", "")
        logging.info("article_id: ", _article_id)
        logging.info("paragraph_id: ", _paragraph_id)

        url = "http://"+STP+"/blogs/paragraphs/" + _paragraph_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _paragraph = json_decode(response.body)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/edit-paragraph.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,travel_type=_travel_type,
                article_id=_article_id,
                paragraph=_paragraph)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _article_id = self.get_argument("article_id", "")
        _paragraph_id = self.get_argument("paragraph_id", "")
        _type = self.get_argument("type", "")
        _content = self.get_argument("content", "")
        logging.info("got paragraph_id %r", _paragraph_id)
        logging.info("got type %r", _type)
        logging.info("got content %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_paragraph_id, params)
            data = {"articleId": _article_id, "id": _paragraph_id, "type": _type, "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="PUT", body=_json)
            logging.info("got response %r", response.body)

            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class EditParagraphRawHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _paragraph_id = self.get_argument("id", "")
        logging.info("article_id: ", _article_id)
        logging.info("paragraph_id: ", _paragraph_id)

        url = "http://"+STP+"/blogs/paragraphs/" + _paragraph_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _paragraph = json_decode(response.body)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/edit-paragraph-raw.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,travel_type=_travel_type,
                article_id=_article_id,
                paragraph=_paragraph)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _paragraph_id = self.get_argument("paragraph_id", "")
        _content = self.get_argument("content", "")
        logging.info("got article_id %r", _article_id)
        logging.info("got paragraph_id %r", _paragraph_id)
        logging.info("got content %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_paragraph_id, params)
            data = {"articleId": _article_id, "id": _paragraph_id, "type": "raw", "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="PUT", body=_json)
            logging.info("got response %r", response.body)

            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class EditParagraphImgHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _travel_id = self.get_argument("travel_id")
        _travel_type = self.get_argument("travel_type")
        _article_id = self.get_argument("article_id", "")
        _paragraph_id = self.get_argument("id", "")
        logging.info("article_id: ", _article_id)
        logging.info("paragraph_id: ", _paragraph_id)

        url = "http://"+STP+"/blogs/paragraphs/" + _paragraph_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _paragraph = json_decode(response.body)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('blog/edit-paragraph-img.html',
                vendor_id=vendor_id,
                my_account=my_account,
                budge_num=budge_num,
                travel_id=_travel_id,travel_type=_travel_type,
                article_id=_article_id,
                paragraph=_paragraph)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _article_id = self.get_argument("article_id", "")
        _paragraph_id = self.get_argument("paragraph_id", "")
        logging.info("article_id: ", _article_id)
        logging.info("paragraph_id: ", _paragraph_id)
        _content = self.get_argument("content", "")
        logging.info("got img_url %r", _content)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_paragraph_id, params)
            data = {"articleId": _article_id, "id": _paragraph_id, "type": "img", "content": _content}
            _json = json_encode(data)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="PUT", body=_json)
            logging.info("got response %r", response.body)

            if _travel_type == 'activity':
                self.redirect('/vendors/' + vendor_id + '/activitys/' + _travel_id + '/detail/step7?scroll_to='+_paragraph_id)
            else:
                self.redirect('/vendors/' + vendor_id + '/trip_router/' + _travel_id + '/edit/step2?scroll_to='+_paragraph_id)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class UpParagraphHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _article_id = (self.request.arguments['articleId'])[0]
        _paragraph_id = (self.request.arguments['id'])[0]
        logging.info("got paragraph_id %r", _paragraph_id)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_paragraph_id+"/up", params)
            http_client = HTTPClient()
            data = {"articleId": _article_id}
            _json = json_encode(data)
            response = http_client.fetch(url, method="PUT", body=_json)
            logging.info("got response %r", response.body)

            self.finish("ok")
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class DownParagraphHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _article_id = (self.request.arguments['articleId'])[0]
        _paragraph_id = (self.request.arguments['id'])[0]
        logging.info("got paragraph_id %r", _paragraph_id)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_paragraph_id+"/down", params)
            http_client = HTTPClient()
            data = {"articleId": _article_id}
            _json = json_encode(data)
            response = http_client.fetch(url, method="PUT", body=_json)
            logging.info("got response %r", response.body)

            self.finish("ok")
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class DelParagraphHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        _ticket = self.get_secure_cookie("session_ticket")
        _article_id = (self.request.arguments['articleId'])[0]
        _paragraph_id = (self.request.arguments['id'])[0]
        logging.info("got paragraph_id %r", _paragraph_id)

        try:
            params = {"X-Session-Id": _ticket}
            url = url_concat("http://"+STP+"/blogs/paragraphs/"+_paragraph_id, params)
            http_client = HTTPClient()
            response = http_client.fetch(url, method="DELETE")
            logging.info("got response %r", response.body)

            self.finish("ok")
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail =='HTTP 401: Unauthorized':
                self.redirect('/auth/logout')


class EditArticleHandler(BaseHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        _article_id = (self.request.arguments['id'])[0]
        logging.info("article_id: ", _article_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        url = "http://"+STP+"/blogs/articles/" + _article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _article = json_decode(response.body)

        self.render('blog/edit-article.html', article=_article)

    def post(self):
        _ticket = self.get_secure_cookie("session_ticket")
        _id = (self.request.arguments['articleId'])[0]
        _title = (self.request.arguments['title'])[0]
        _content = (self.request.arguments['content'])[0]
        _img_url = (self.request.arguments['imgUrl'])[0]
        logging.info("got title %r", _title)
        logging.info("got title %r", _content)
        logging.info("got title %r", _img_url)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        params = {"X-Session-Id": _ticket}
        url = url_concat("http://"+STP+"/blogs/articles/"+_id, params)
        data = {"title": _title, "content": _content, "imgUrl": _img_url}
        _json = json_encode(data)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="PUT", body=_json)
        logging.info("got response %r", response.body)

        _timestamp = long(time.time() * 1000)
        params = {"before": _timestamp, "limit": 20}
        url = url_concat("http://"+STP+"/blogs/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _articles = json_decode(response.body)

        for _article in _articles:
            _timestamp = _article["timestamp"]
            _datetime = timestamp_datetime(_timestamp / 1000)
            _article["timestamp"] = _datetime

        self.render('blog/my-articles.html', articles=_articles)


class ArticleHandler(tornado.web.RequestHandler):
    def get(self):
        _article_id = (self.request.arguments['id'])[0]
        logging.info("article_id: ", _article_id)

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        url = "http://"+STP+"/blogs/articles/" + _article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _article = json_decode(response.body)
        _timestamp = _article["timestamp"]
        _datetime = timestamp_datetime(_timestamp / 1000)
        _article["timestamp"] = _datetime

        url = "http://"+STP+"/blogs/my-articles/" + _article_id + "/paragraphs"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _paragraphs = json_decode(response.body)

        _random = random.randint(1, 9)
        _bgImgRandom = "/static/images/title-bkg/"+str(_random)+".jpg"
        self.render('blog/article.html', article=_article, paragraphs=_paragraphs, bgImgRandom = _bgImgRandom)


class AjaxArticlesHandler(tornado.web.RequestHandler):
    def get(self):
        _last_timestamp = (self.request.arguments['last'])[0] # datetime as 2016-02-12 15:29
        print "last_timestamp: "+_last_timestamp

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()

        if _last_timestamp == None:
            _timestamp = long(time.time() * 1000)
            print _timestamp
        elif _last_timestamp == '':
            _timestamp = long(time.time() * 1000)
            print _timestamp
        else:
            _timestamp = datetime_timestamp(_last_timestamp) * 1000
            print _timestamp

        params = {"before": _timestamp, "limit": 20}
        url = url_concat("http://"+STP+"/blogs/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _articles = json_decode(response.body)

        for _article in _articles:
            _timestamp = _article["timestamp"]
            _datetime = timestamp_datetime(_timestamp / 1000)
            _article["timestamp"] = _datetime

        self.finish(json.dumps(_articles))


class AjaxMyArticlesHandler(tornado.web.RequestHandler):
    def get(self):
        _ticket = self.get_secure_cookie("session_ticket")
        _last_timestamp = (self.request.arguments['last'])[0] # datetime as 2016-02-12 15:29
        print _last_timestamp

        session_ticket = self.get_session_ticket()
        my_account = self.get_account_info()
        
        if _last_timestamp == None:
            _timestamp = long(time.time() * 1000)
            print _timestamp
        elif _last_timestamp == '':
            _timestamp = long(time.time() * 1000)
            print _timestamp
        else:
            _timestamp = datetime_timestamp(_last_timestamp) * 1000
            print _timestamp

        params = {"X-Session-Id": _ticket, "before": _timestamp, "limit": 20}
        url = url_concat("http://"+STP+"/blogs/my-articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        _articles = json_decode(response.body)

        for _article in _articles:
            _timestamp = _article["timestamp"]
            _datetime = timestamp_datetime(_timestamp / 1000)
            _article["timestamp"] = _datetime

        self.finish(json.dumps(_articles))
