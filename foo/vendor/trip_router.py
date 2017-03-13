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
import sys
import os
import uuid
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat

from comm import *
from dao import budge_num_dao
from dao import trip_router_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import evaluation_dao
from dao import triprouter_share_dao
from dao import club_dao
from global_const import *


# /
class TripRouterIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        ops = self.get_ops_info()
        logging.info("got ops %r in uri", ops)

        self.redirect('/vendors/' + ops['club_id'] + '/trip_router')


# /vendors/<string:vendor_id>/triprouters
class VendorTriprouterListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        logging.info("got ops %r in uri", ops)

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        triprouters = trip_router_dao.trip_router_dao().query_by_vendor(vendor_id)

        for triprouter in triprouters:
            for category in categorys:
                if category['_id'] == triprouter['category']:
                    triprouter['category'] = category['title']
                    break

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/trip-router-list.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                triprouters=triprouters)


# /vendors/<string:vendor_id>/trip_router/create
class VendorTriprouterCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/trip-router-create.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                categorys=categorys)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        _title = self.get_argument("title", "")
        _bk_img_url = self.get_argument("bk_img_url", "")
        _category = self.get_argument("category", "")
        _location = self.get_argument("location", "")
        _distance = self.get_argument("distance", "")
        _strength = self.get_argument("strength", "")
        _scenery = self.get_argument("scenery", "")
        _road_info = self.get_argument("road_info", "")
        _kickoff = self.get_argument("kickoff", "")

        logging.debug("got param title %r", _title)

        _id = str(uuid.uuid1()).replace('-', '')
        logging.info("create triprouter _id %r", _id)
        triprouters = {"_id":_id, "vendor_id":vendor_id,
                "title":_title, "bk_img_url":_bk_img_url, "category":_category, "location":_location,
                "distance":_distance, "strength":_strength, "scenery":_scenery, "road_info":_road_info,
                "kickoff":_kickoff, "score":10, "open":False}

        trip_router_dao.trip_router_dao().create(triprouters);

        article = {'title':_title, 'subtitle':_location, 'img':_bk_img_url,'paragraphs':''}
        _json = json_encode(article)
        headers = {"Authorization":"Bearer "+access_token}
        url = "http://api.7x24hs.com/api/articles"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)
        article = json_decode(response.body)
        article_id = article['_id']
        _paragraphs = ''

        trip_router_dao.trip_router_dao().update({'_id':_id, 'article_id':article_id})

        # create blog article
        # _ticket = self.get_secure_cookie("session_ticket")
        # params = {"X-Session-Id": _ticket}
        # url = url_concat("http://" + STP + "/blogs/articles", params)
        # data = {"title": _title, "content": "", "imgUrl": _bk_img_url}
        # _json = json_encode(data)
        # http_client = HTTPClient()
        # response = http_client.fetch(url, method="POST", body=_json)
        # logging.info("got response %r", response.body)
        # _article_id = json_decode(response.body)
        # logging.info("got _article_id %r", _article_id)
        #
        # json = {"_id":_id, "article_id":_article_id}
        # trip_router_dao.trip_router_dao().update(json)


        self.redirect('/vendors/' + vendor_id + '/trip_router')

 #/vendors/<string:vendor_id>/trip_router/<string:trip_router_id>/delete
class VendorTriprouterDeleteHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip-router_id %r in uri", trip_router_id)

        ops = self.get_ops_info()

        trip_router_dao.trip_router_dao().delete(trip_router_id)

        self.redirect('/vendors/' + vendor_id + '/trip_router')

 #/vendors/<string:vendor_id>/trip_router/<string:trip_router_id>/edit/step1
class VendorTriprouterEditStep1Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip-router_id %r in edit step1", trip_router_id)

        ops = self.get_ops_info()

        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)

        self.render('vendor/trip-router-edit-step1.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                triprouter=triprouter, categorys=categorys)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r ~~~~~~in uri", vendor_id)
        logging.info("got trip_router_id %r @@@@@@in uri", trip_router_id)

        ops = self.get_ops_info()

        _title = self.get_argument("title", "")
        _bk_img_url = self.get_argument("bk_img_url", "")
        _category = self.get_argument("category", "")
        _location = self.get_argument("location", "")
        _distance = self.get_argument("distance", "")
        _strength = self.get_argument("strength", "")
        _scenery = self.get_argument("scenery", "")
        _road_info = self.get_argument("road_info", "")
        _kickoff = self.get_argument("kickoff", "")

        logging.info("update triprouter _id %r", trip_router_id)
        json = {"_id":trip_router_id, "vendor_id":vendor_id,
                "title":_title, "bk_img_url":_bk_img_url, "category":_category, "location":_location,
                "distance":_distance, "strength":_strength, "scenery":_scenery, "road_info":_road_info,
                "kickoff":_kickoff, "score":10}

        trip_router_dao.trip_router_dao().update(json)

        self.redirect('/vendors/' + vendor_id + '/trip_router/' + trip_router_id + '/edit/step1')

 #/vendors/<string:vendor_id>/trip_router/<string:trip_router_id>/edit/step2
class VendorTriprouterEditStep2Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip_router_id %r in edit step2", trip_router_id)

        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)
        # _article_id = triprouter['article_id']

        _article_id = None
        _paragraphs = None
        if triprouter.has_key('article_id'):
            _article_id = triprouter['article_id']
            url = "http://api.7x24hs.com/api/articles/" + _article_id
            http_client = HTTPClient()
            response = http_client.fetch(url, method="GET")
            logging.info("got response %r", response.body)
            article = json_decode(response.body)
            _paragraphs = article['paragraphs']
        else:
            article = {'title':triprouter['title'], 'subtitle':triprouter['location'], 'img':triprouter['bk_img_url'],'paragraphs':''}
            _json = json_encode(article)
            headers = {"Authorization":"Bearer "+access_token}
            url = "http://api.7x24hs.com/api/articles"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", headers=headers, body=_json)
            logging.info("got response %r", response.body)
            article = json_decode(response.body)
            article_id = article['_id']
            _paragraphs = ''

            trip_router_dao.trip_router_dao().update({'_id':trip_router_id, 'article_id':article_id})

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/trip-router-edit-step2.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                triprouter=triprouter,
                travel_id=trip_router_id,
                article_id=_article_id,
                paragraphs=_paragraphs)

    def post(self,vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip_router_id %r in uri", trip_router_id)

        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)

        content = self.get_argument("content","")
        logging.info("got content %r", content)

        _article_id = None
        if triprouter.has_key('article_id'):
            _article_id = triprouter['article_id']
        article = {'title':triprouter['title'], 'subtitle':triprouter['location'], 'img':triprouter['bk_img_url'],'paragraphs':content}
        _json = json_encode(article)
        headers = {"Authorization":"Bearer "+access_token}
        url = "http://api.7x24hs.com/api/articles/"+_article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/trip_router/' + trip_router_id + '/edit/step2')


 #/vendors/<string:vendor_id>/trip_router/<string:trip_router_id>/clone
class VendorTriprouterCloneHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip_router_id %r in uri", trip_router_id)

        ops = self.get_ops_info()

        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)
        article_id = triprouter['article_id']
        logging.info("got article_id %r", article_id)

        # create activity
        _activity_id = str(uuid.uuid1()).replace('-', '')
        _timestamp = time.time()
        _json = {"_id":_activity_id, "vendor_id":vendor_id,
                "status":ACTIVITY_STATUS_DRAFT, "popular":False,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "title":triprouter['title'],
                "bk_img_url":triprouter['bk_img_url'],
                "category":triprouter['category'],
                "triprouter":triprouter['_id'],
                "location":triprouter['location'],
                "hidden":False,"cash_only":False,
                "begin_time":_timestamp, "end_time":_timestamp, "apply_end_time":_timestamp,
                "distance":triprouter['distance'],
                "strength":triprouter['strength'],
                "scenery":triprouter['scenery'],
                "road_info":triprouter['road_info'],
                "kickoff":triprouter['kickoff'],
                "base_fee_template":[],
                "ext_fee_template":[],
                "member_min":0,
                "member_max":0,
                "notes":''}
        activity_dao.activity_dao().create(_json)

        # create wechat qrcode
        activity_url = WX_NOTIFY_DOMAIN + "/bf/wx/vendors/" + vendor_id + "/activitys/" + _activity_id
        logging.info("got activity_url %r", activity_url)
        data = {"url": activity_url}
        _json = json_encode(data)
        logging.info("got ——json %r", _json)
        http_client = HTTPClient()
        response = http_client.fetch(QRCODE_CREATE_URL, method="POST", body=_json)
        logging.info("got response %r", response.body)
        qrcode_url = response.body
        logging.info("got qrcode_url %r", qrcode_url)

        wx_qrcode_url = "http://bike-forever.b0.upaiyun.com/vendor/wx/2016/7/21/66a75009-e60e-44b1-80f7-bf4a9d95525a.jpg"
        json = {"_id":_activity_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "qrcode_url":qrcode_url, "wx_qrcode_url":wx_qrcode_url}
        group_qrcode_dao.group_qrcode_dao().create(json)

        # create blog article
        _ticket = self.get_secure_cookie("session_ticket")
        params = {"X-Session-Id": _ticket}
        _json = json_encode(params)
        url = "http://"+STP+"/blogs/articles/" + article_id + "/clone"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", body=_json)
        logging.info("got response %r", response.body)
        new_article_id = json_decode(response.body)
        logging.info("got new_article_id %r", new_article_id)

        _json = {"_id":_activity_id, "article_id":new_article_id}
        activity_dao.activity_dao().update(_json)

        # create cretificate
        _cert_template_id = str(uuid.uuid1()).replace('-', '')
        _timestamp = time.time()
        json = {"_id":_activity_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "distance":0, "hours":0, "height":0, "slope_length":0, "speed":0,
                "road_map_url":"", "contour_map_url":""}
        cret_template_dao.cret_template_dao().create(json);

        # create bonus
        json = {"_id":_activity_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "activity_shared":0, "cret_shared":0}
        bonus_template_dao.bonus_template_dao().create(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/draft')


 #/vendors/<string:vendor_id>/trip_router/<string:trip_router_id>/activitylist
class VendorTriprouterActivityListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        activitys = activity_dao.activity_dao().query_by_triprouter(trip_router_id)
        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/trip-router-activitylist.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                triprouter=triprouter,
                activitys=activitys)


#/vendors/<string:vendor_id>/trip_router/<string:trip_router_id>/evallist
class VendorTriprouterEvalListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)
        evaluations = evaluation_dao.evaluation_dao().query_by_triprouter(trip_router_id)
        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/trip-router-evallist.html',
                vendor_id=vendor_id,
                ops=ops,
                triprouter=triprouter,
                budge_num=budge_num,
                evaluations=evaluations)


 #/vendors/<string:vendor_id>/trip_router/<string:trip_router_id>/share/set
class VendorTriprouterOpenSetHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip-router_id %r in uri", trip_router_id)

        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)

        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        json = {"_id":trip_router_id, "open":True}
        trip_router_dao.trip_router_dao().updateOpenStatus(json)

        _article_id = None
        if triprouter.has_key('article_id'):
            _article_id = triprouter['article_id']
        headers = {"Authorization":"Bearer "+access_token}
        url = "http://api.7x24hs.com/api/articles/" + _article_id + "/publish"
        http_client = HTTPClient()
        _json = json_encode(headers)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        ids = {'ids':['8853422e03a911e7998c00163e023e51']}
        _json = json_encode(ids)
        headers = {"Authorization":"Bearer "+access_token}
        url = "http://api.7x24hs.com/api/articles/" + _article_id + "/categories"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/trip_router')

class VendorTriprouterOpenCancelHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip-router_id %r in uri", trip_router_id)

        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)

        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        _article_id = None
        if triprouter.has_key('article_id'):
            _article_id = triprouter['article_id']
        headers = {"Authorization":"Bearer "+access_token}
        url = "http://api.7x24hs.com/api/articles/" + _article_id + "/unpublish"
        http_client = HTTPClient()
        _json = json_encode(headers)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        json = {"_id":trip_router_id, "open":False}
        trip_router_dao.trip_router_dao().updateOpenStatus(json)

        self.redirect('/vendors/' + vendor_id + '/trip_router')


# 其他俱乐部开放的项目
class VendorTriprouterShareListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        # categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        triprouters = trip_router_dao.trip_router_dao().query_by_open(vendor_id)
        triprouters_share = triprouter_share_dao.triprouter_share_dao().query_by_vendor(vendor_id)

        # 在所有开放的线路中剔除掉自己开放的
        for triprouter in triprouters:
            if(triprouter['vendor_id'] == vendor_id):
                triprouters.remove(triprouter)
                break

        # 加share属性，区别一个自己是否已经分享了别人开放的这个线路
        for triprouter in triprouters:
            club = club_dao.club_dao().query(triprouter['vendor_id'])
            triprouter['club']= club['club_name']
            triprouter['share'] = False

            for triprouter_share in triprouters_share:
                if(triprouter['_id']==triprouter_share['triprouter']):
                    triprouter['share'] = True
                    break

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/trip-router-share.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                triprouters=triprouters)


class VendorTriprouterShareSetHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip-router_id %r in uri", trip_router_id)

        ops = self.get_ops_info()

        # 设置别人开放的线路为自己所用
        triprouter = trip_router_dao.trip_router_dao().query(trip_router_id)
        club = club_dao.club_dao().query(triprouter['vendor_id'])

        _id = str(uuid.uuid1()).replace('-', '')
        json = {"_id":_id, "triprouter":trip_router_id,
                "share":True,"vendor_id":vendor_id, "bk_img_url":triprouter['bk_img_url'],
                "title":triprouter['title'],"club":club['club_name'],"score":triprouter['score']}

        triprouter_share_dao.triprouter_share_dao().create(json)

        self.redirect('/vendors/' + vendor_id + '/trip_router/share')

class VendorTriprouterShareCancelHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, trip_router_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got trip_router_id %r in uri", trip_router_id)

        ops = self.get_ops_info()

        triprouter_share = triprouter_share_dao.triprouter_share_dao().query_by_triprouter_vendor(trip_router_id,vendor_id)
        triprouter_share_dao.triprouter_share_dao().delete(triprouter_share['_id'])

        self.redirect('/vendors/' + vendor_id + '/trip_router/share')


class VendorTriprouterUseListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        triprouters_me = trip_router_dao.trip_router_dao().query_by_vendor(vendor_id)
        triprouters_share = triprouter_share_dao.triprouter_share_dao().query_by_vendor(vendor_id)

        # 处理一下自己线路
        for triprouter in triprouters_me:
            club = club_dao.club_dao().query(triprouter['vendor_id'])
            triprouter['club'] = club['club_name']
            triprouter['share'] = False

        triprouters = triprouters_me + triprouters_share

        budge_num = budge_num_dao.budge_num_dao().query(vendor_id)
        self.render('vendor/trip-router-use.html',
                vendor_id=vendor_id,
                ops=ops,
                budge_num=budge_num,
                triprouters=triprouters)
