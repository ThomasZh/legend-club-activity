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
from qrcode import *
import sys
import os
import math
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat

from comm import *

from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import cret_dao
from dao import bonus_template_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import vendor_member_dao
from dao import trip_router_dao
from dao import evaluation_dao
from dao import activity_share_dao
from dao import vendor_wx_dao

from global_const import *


# /vendors/<string:vendor_id>/activitys/draft
class VendorActivityDraftHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)

        _status = ACTIVITY_STATUS_DRAFT
        activitys = self.get_activities(vendor_id, _status, 1, 20)


        # before = time.time();
        # activitys = activity_dao.activity_dao().query_pagination_by_status(
        #         vendor_id, ACTIVITY_STATUS_DRAFT, before, PAGE_SIZE_LIMIT)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            # for category in categorys:
            #     if category['_id'] == activity['category']:
            #         activity['category'] = category['title']
            #         break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-draft.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


# /vendors/<string:vendor_id>/activitys/pop
class VendorActivityPopHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        before = time.time();
        limit = 20
        activitys = activity_dao.activity_dao().query_by_popular(vendor_id)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-pop.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


# /vendors/<string:vendor_id>/activitys/doing
class VendorActivityDoingHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        before = time.time();
        activitys = activity_dao.activity_dao().query_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_DOING, before, PAGE_SIZE_LIMIT)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-doing.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


# /vendors/<string:vendor_id>/activitys/recruit
class VendorActivityRecruitHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        before = time.time();
        activitys = activity_dao.activity_dao().query_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_RECRUIT, before, PAGE_SIZE_LIMIT)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-recruit.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


class VendorActivityRecruitNotHiddenHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        before = time.time();
        activitys = activity_dao.activity_dao().query_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_RECRUIT, before, PAGE_SIZE_LIMIT)

        for activity in activitys:
            # 剔除掉隐藏活动
            if activity['hidden']:
                activitys.remove(activity)
            # 加open属性
            if not activity.has_key('open'):
                activity['open'] = False

            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-recruit-nothidden.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


class VendorActivityOpenSetHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        json = {"_id":activity_id, "open":True}
        activity_dao.activity_dao().updateOpenStatus(json)

        self.redirect('/vendors/' + vendor_id + '/activitys/recruit-nothidden')


class VendorActivityOpenCancelHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        json = {"_id":activity_id, "open":False}
        activity_dao.activity_dao().updateOpenStatus(json)

        # 取消开放的活动不能在分享列表里
        activity_share_dao.activity_share_dao().delete_by_activity(activity_id)

        self.redirect('/vendors/' + vendor_id + '/activitys/recruit-nothidden')


# 联盟中其他俱乐部开放了的活动
class VendorActivityLeagueShareHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        # activitys = activity_dao.activity_dao().query_by_open()
        activitys = activity_dao.activity_dao().query_by_open_status_notme(ACTIVITY_STATUS_RECRUIT,vendor_id)
        activitys_share = activity_share_dao.activity_share_dao().query_by_vendor(vendor_id)

        # 加share属性，区别一个自己是否已经分享了别人开放的这个活动
        for activity in activitys:
            # 取俱乐部名称
            club_id = activity['vendor_id']
            club = get_club_info(access_token,club_id)
            if club:
                activity['club'] = club['name']
            else:
                activity['club'] = ""
            activity['share'] = False

            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y

            for activity_share in activitys_share:
                if(activity['_id']==activity_share['activity']):
                    activity['share'] = True
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-league-share.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


class VendorActivityShareSetHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        # 设置别人开放的活动为自己所用
        activity = activity_dao.activity_dao().query(activity_id)

        # vendor_id是我,club是活动的创建者
        _id = str(uuid.uuid1()).replace('-', '')
        json = {"_id":_id, "activity":activity_id,
                "share":True,"vendor_id":vendor_id, "bk_img_url":activity['bk_img_url'],
                "title":activity['title'],"club":activity['vendor_id']}

        activity_share_dao.activity_share_dao().create(json)

        self.redirect('/vendors/' + vendor_id + '/activitys/league/share')


class VendorActivityShareCancelHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_share = activity_share_dao.activity_share_dao().query_by_activity_vendor(activity_id,vendor_id)
        activity_share_dao.activity_share_dao().delete(activity_share['_id'])

        self.redirect('/vendors/' + vendor_id + '/activitys/league/share')


# 我会员所见所有活动
class VendorActivityLeagueRecruitHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)

        # 查询自己在招募中的活动
        activitys_me = activity_dao.activity_dao().query_by_vendor_status(vendor_id,ACTIVITY_STATUS_RECRUIT)
        activitys_share = activity_share_dao.activity_share_dao().query_by_vendor(vendor_id)

        # 处理一下自己活动
        for activity in activitys_me:
            # club = club_dao.club_dao().query(activity['vendor_id'])
            activity['share'] = False
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            activity['club'] = ops['club_name']

        # 分享的活动中如果不是在招募中了就删除掉
        for share in activitys_share:
            _id = share['activity']
            act = activity_dao.activity_dao().query(_id)
            # 分享了别人俱乐部招募中的活动
            if act['status'] != ACTIVITY_STATUS_RECRUIT:
                logging.info("===========%r",act['status'])
                # activitys_share.remove(share)
                activity_share_dao.activity_share_dao().delete(share['_id'])

        # 重新查询分享了的活动
        activitys_share_new = activity_share_dao.activity_share_dao().query_by_vendor(vendor_id)
        for share in activitys_share_new:
            _id = share['activity']
            act = activity_dao.activity_dao().query(_id)
            share['begin_time'] = timestamp_date(float(act['begin_time'])) # timestamp -> %m/%d/%Y
            # 取俱乐部名称
            club_id = share['club']
            club = get_club_info(access_token,club_id)
            if club:
                share['club'] = club['name']
            else:
                share['club'] = ""

        activitys = activitys_me + activitys_share_new

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-recruit-all.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


#查看别人分享活动的招募帖 VendorActivityLeagueDemoHandler
class VendorActivityLeagueDemoHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()
        _activity = activity_dao.activity_dao().query(activity_id)
        # 按报名状况查询每个活动的当前状态：
        # 0: 报名中, 1: 已成行, 2: 已满员, 3: 已结束
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

        _bonus_template = bonus_template_dao.bonus_template_dao().query(_activity['_id'])

        article = self.get_article(_activity['_id'])
        if not article:
            article = {'_id':_activity['_id'], 'title':_activity['title'], 'subtitle':_activity['location'], 'img':_activity['bk_img_url'],'paragraphs':''}
            self.create_article(article)

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-demo.html',
                    vendor_id=vendor_id,
                    ops=ops,
                    counter=counter,
                    bonus_template=_bonus_template,
                    article=article,
                    activity=_activity)


# /vendors/<string:vendor_id>/activitys/canceled
class VendorActivityCanceledHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        before = time.time();
        activitys = activity_dao.activity_dao().query_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_CANCELED, before, PAGE_SIZE_LIMIT)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-canceled.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


# /vendors/<string:vendor_id>/activitys/completed
class VendorActivityCompletedHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        before = 0
        activitys = activity_dao.activity_dao().query_pagination_by_status(
                vendor_id, ACTIVITY_STATUS_COMPLETED, before, PAGE_SIZE_LIMIT)
        for activity in activitys:
            activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
            for category in categorys:
                if category['_id'] == activity['category']:
                    activity['category'] = category['title']
                    break

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-completed.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activitys=activitys)


# /vendors/<string:vendor_id>/activitys/create/step1
class VendorActivityCreateStep1Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        triprouters = trip_router_dao.trip_router_dao().query_by_vendor(vendor_id)
        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-create-step1.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                triprouters=triprouters,
                categorys=categorys)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_secure_cookie("access_token")

        ops = self.get_ops_info()

        _title = self.get_argument("title", "")
        _bk_img_url = self.get_argument("bk_img_url", "")
        _category = self.get_argument("category", "")
        _triprouter = self.get_argument("triprouter","")

        hidden = self.get_argument("hidden", "")
        logging.info("got hidden %r", hidden)
        if hidden == 'true':
            hidden = True
        else:
            hidden = False

        cash_only = self.get_argument("cash_only", "")
        logging.info("got cash_only %r", cash_only)
        if cash_only == 'true':
            cash_only = True
        else:
            cash_only = False

        location = self.get_argument("location", "")
        _begin_time = self.get_argument("begin_time", "")
        _begin_time = float(date_timestamp(_begin_time)) # %m/%d/%Y -> timestamp
        _end_time = self.get_argument("end_time", "")
        _end_time = float(date_timestamp(_end_time)) # %m/%d/%Y -> timestamp
        _apply_end_time = self.get_argument("apply_end_time", "")
        _apply_end_time = float(date_timestamp(_apply_end_time)) # %m/%d/%Y -> timestamp
        _distance = self.get_argument("distance", "")
        _strength = self.get_argument("strength", "")
        _scenery = self.get_argument("scenery", "")
        _road_info = self.get_argument("road_info", "")
        _kickoff = self.get_argument("kickoff", "")
        _member_min = self.get_argument("member_min", "")
        _member_max = self.get_argument("member_max", "")

        # create activity
        # _activity_id = str(uuid.uuid1()).replace('-', '')
        # json = {"_id":_activity_id, "vendor_id":vendor_id,
        #         "status":ACTIVITY_STATUS_DRAFT, "popular":False,
        #         "hidden":hidden, "cash_only":cash_only,
        #         "create_time":_timestamp, "last_update_time":_timestamp,
        #         "title":_title, "bk_img_url":_bk_img_url, "category":_category, "triprouter":_triprouter, "location":location,
        #         "begin_time":_begin_time, "end_time":_end_time, "apply_end_time":_apply_end_time,
        #         "distance":_distance, "strength":_strength, "scenery":_scenery, "road_info":_road_info, "kickoff":_kickoff,
        #         "ext_fee_template":[], "base_fee_template":[],
        #         "member_min":_member_min, "member_max":_member_max, "notes":'' }
        # activity_dao.activity_dao().create(json)

        activity = {
            "club_id":vendor_id,
            "title":_title,
            "subtitle":_distance,
            "img":_bk_img_url,
            "category_id":_category,
            "begin_time":_begin_time, "end_time":_end_time, "apply_end_time":_apply_end_time,
            "mileage":_distance,
            "amount":0,
            "private_status":hidden,
            "cash_only":cash_only,
            "strength":_strength, "scenery":_scenery, "road_info":_road_info, "kickoff":_kickoff,
            "ext_fee_template":[], "base_fee_template":[],
            "member_min":_member_min, "member_max":_member_max,
            "notes":''
        }
        headers = {"Authorization":"Bearer "+access_token}
        url = API_DOMAIN + "/api/activities"
        _json = json_encode(activity)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("create activity response.body=[%r]", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        _activity_id = rs["_id"]

        article = {'_id':_activity_id, 'title':_title, 'subtitle':location, 'img':_bk_img_url,'paragraphs':''}
        self.create_article(article)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_notify_domain = wx_app_info['wx_notify_domain']
        # create wechat qrcode
        activity_url = wx_notify_domain + "/bf/wx/vendors/" + vendor_id + "/activitys/" + _activity_id
        logging.info("got activity_url %r", activity_url)
        data = {"url": activity_url}
        _json = json_encode(data)
        logging.info("got ——json %r", _json)
        http_client = HTTPClient()
        response = http_client.fetch(QRCODE_CREATE_URL, method="POST", body=_json)
        logging.info("got response %r", response.body)
        qrcode_url = response.body
        logging.info("got qrcode_url %r", qrcode_url)

        _timestamp = time.time()
        wx_qrcode_url = "http://bike-forever.b0.upaiyun.com/vendor/wx/2016/7/21/66a75009-e60e-44b1-80f7-bf4a9d95525a.jpg"
        json = {"_id":_activity_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "qrcode_url":qrcode_url, "wx_qrcode_url":wx_qrcode_url}
        group_qrcode_dao.group_qrcode_dao().create(json)

        # create cretificate
        json = {"_id":_activity_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "distance":0, "hours":0, "height":0, "slope_length":0, "speed":0,
                "road_map_url":"", "contour_map_url":""}
        cret_template_dao.cret_template_dao().create(json)

        # create bonus
        json = {"_id":_activity_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "activity_shared":0, "cret_shared":0}
        bonus_template_dao.bonus_template_dao().create(json)

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-create-step2.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activity_id=_activity_id)


class VendorActivityCreateStep2Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-create-step2.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activity_id=activity_id)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        slope_length = self.get_argument("slope_length", "")
        distance = self.get_argument("distance", "")
        hours = self.get_argument("hours", "")
        height = self.get_argument("height", "")
        speed = self.get_argument("speed", "")
        road_map_url = self.get_argument("road_map_url", "")
        contour_map_url = self.get_argument("contour_map_url", "")

        _timestamp = time.time()
        json = {"_id":activity_id,
                "last_update_time":_timestamp,
                "slope_length":slope_length, "distance":distance, "hours":hours, "height":height, "speed":speed,
                "road_map_url":road_map_url, "contour_map_url":contour_map_url}
        cret_template_dao.cret_template_dao().update(json);

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-create-step3.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activity_id=activity_id)


class VendorActivityCreateStep3Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-create-step3.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                activity_id=activity_id)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_shared = self.get_argument("activity_shared", "")
        cret_shared = self.get_argument("cret_shared", "")

        _timestamp = time.time()
        json = {"_id":activity_id,
                "last_update_time":_timestamp,
                "activity_shared":activity_shared, "cret_shared":cret_shared}
        bonus_template_dao.bonus_template_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/draft')


class VendorActivityDetailStep1Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity = self.get_activity(activity_id)
        # _activity = activity_dao.activity_dao().query(activity_id)
        activity['begin_time'] = timestamp_date(float(activity['begin_time'])) # timestamp -> %m/%d/%Y
        activity['end_time'] = timestamp_date(float(activity['end_time'])) # timestamp -> %m/%d/%Y
        activity['apply_end_time'] = timestamp_date(float(activity['apply_end_time'])) # timestamp -> %m/%d/%Y

        triprouters = trip_router_dao.trip_router_dao().query_by_vendor(vendor_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        try:
            bonus_template['activity_shared']
        except:
            bonus_template['activity_shared'] = 0
        try:
            bonus_template['cret_shared']
        except:
            bonus_template['cret_shared'] = 0
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step1.html',
                vendor_id=vendor_id,
                ops=ops,
                activity_id=activity_id,
                counter=counter, activity_counter=activity_counter,
                triprouters=triprouters,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template)


    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        _title = self.get_argument("title", "")
        _bk_img_url = self.get_argument("bk_img_url", "")
        _category = self.get_argument("category", "")
        _triprouter = self.get_argument("triprouter","")
        hidden = self.get_argument("hidden", "")
        logging.info("got hidden %r", hidden)
        if hidden == 'true':
            hidden = True
        else:
            hidden = False
        location = self.get_argument("location", "")
        _begin_time = self.get_argument("begin_time", "")
        _begin_time = float(date_timestamp(_begin_time)) # %m/%d/%Y -> timestamp
        _end_time = self.get_argument("end_time", "")
        _end_time = float(date_timestamp(_end_time)) # %m/%d/%Y -> timestamp
        _apply_end_time = self.get_argument("apply_end_time", "")
        _apply_end_time = float(date_timestamp(_apply_end_time)) # %m/%d/%Y -> timestamp
        _distance = self.get_argument("distance", "")
        _strength = self.get_argument("strength", "")
        _scenery = self.get_argument("scenery", "")
        _road_info = self.get_argument("road_info", "")
        _kickoff = self.get_argument("kickoff", "")
        _member_min = self.get_argument("member_min", "")
        _member_max = self.get_argument("member_max", "")
        logging.info("got _title %r", _title)

        _timestamp = time.time()
        json = {"_id":activity_id,
                "last_update_time":_timestamp,
                "hidden":hidden,
                "title":_title, "bk_img_url":_bk_img_url, "category":_category, "triprouter":_triprouter ,"location":location,
                "begin_time":_begin_time, "end_time":_end_time, "apply_end_time":_apply_end_time,
                "distance":_distance, "strength":_strength, "scenery":_scenery, "road_info":_road_info, "kickoff":_kickoff,
                "member_min":_member_min, "member_max":_member_max}
        activity_dao.activity_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step1')


class VendorActivityDetailStep2Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)
        try:
            qrcode['wx_qrcode_url']
        except:
            json = {"_id":activity_id,"wx_qrcode_url":qrcode['qrcode_url']}
            group_qrcode_dao.group_qrcode_dao().update(json)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_notify_domain = wx_app_info['wx_notify_domain']

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step2.html',
                vendor_id=vendor_id,
                ops=ops,
                wx_notify_domain=wx_notify_domain,
                activity_id=activity_id,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template,
                qrcode=qrcode)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        wx_qrcode_url = self.get_argument("wx_qrcode_url", "")
        logging.info("got wx_qrcode_url----------------- %r", wx_qrcode_url)

        _timestamp = time.time()
        json = {"_id":activity_id,
                "last_update_time":_timestamp,
                "wx_qrcode_url":wx_qrcode_url}
        group_qrcode_dao.group_qrcode_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step2')


class VendorActivityDetailStep3Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step3.html',
                vendor_id=vendor_id,
                ops=ops,
                activity_id=activity_id,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        template_id = self.get_argument("template_id", "")
        logging.info("got template_id %r", template_id)
        distance = self.get_argument("distance", "")
        hours = self.get_argument("hours", "")
        height = self.get_argument("height", "")
        speed = self.get_argument("speed", "")
        road_map_url = self.get_argument("road_map_url", "")
        contour_map_url = self.get_argument("contour_map_url", "")
        logging.info("got road_map_url %r", road_map_url)
        logging.info("got contour_map_url %r", contour_map_url)

        _timestamp = time.time()
        json = {"_id":template_id,
                "last_update_time":_timestamp,
                "distance":distance, "hours":hours, "height":height,
                "speed":speed, "road_map_url":road_map_url, "contour_map_url":contour_map_url}
        cret_template_dao.cret_template_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step3')


class VendorActivityDetailStep4Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step4.html',
                vendor_id=vendor_id,
                ops=ops,
                activity_id=activity_id,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template, bonus_template=bonus_template)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_shared = self.get_argument("activity_shared", "")
        cret_shared = self.get_argument("cret_shared", "")

        _timestamp = time.time()
        json = {"_id":activity_id,
                "last_update_time":_timestamp,
                "activity_shared":activity_shared, "cret_shared":cret_shared}
        bonus_template_dao.bonus_template_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step4')


class VendorActivityDetailStep5Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step5.html',
                vendor_id=vendor_id,
                ops=ops,
                access_token=access_token,
                activity_id=activity_id,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template)


class VendorActivityDetailStep6Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        params = {"filter":"item", "item_id":activity_id, "page":1, "limit":20}
        url = url_concat(API_DOMAIN + "/api/applies", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        applies = rs['data']

        for _apply in applies:
            # 下单时间，timestamp -> %m月%d 星期%w
            _apply['create_time'] = timestamp_datetime(float(_apply['create_time']))
            if _apply['gender'] == 'male':
                _apply['gender'] = u'男'
            else:
                _apply['gender'] = u'女'

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step6.html',
                vendor_id=vendor_id,
                ops=ops,
                activity_id=activity_id,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                applies=applies, bonus=bonus,
                cret_template=cret_template)


class VendorActivityDetailStep7Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        article = self.get_article(activity_id)
        if not article:
            article = {'_id':activity_id, 'title':activity['title'], 'subtitle':activity['location'], 'img':activity['bk_img_url'],'paragraphs':''}
            self.create_article(article)

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step7.html',
                vendor_id=vendor_id,
                ops=ops,
                travel_id=activity_id,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template,
                article=article)


    def post(self,vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        _activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        applys = apply_dao.apply_dao().query_by_activity(activity_id)
        orders = order_dao.order_dao().query_by_activity(activity_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        content = self.get_argument("content","")
        logging.info("got content %r", content)

        article = {'_id':activity_id ,'title':activity['title'], 'subtitle':activity['location'], 'img':activity['bk_img_url'],'paragraphs':content}
        self.update_article(article)

        self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step7')


class VendorActivityDetailStep8Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        for base_fee_template in activity['base_fee_template']:
            base_fee_template['fee'] = float(base_fee_template['fee']) / 100
        for ext_fee_template in activity['ext_fee_template']:
            ext_fee_template['fee'] = float(ext_fee_template['fee']) / 100

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step8.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        # 生成基本服务
        base_serv_names = self.get_arguments("base_serv_name")
        base_serv_fees = self.get_arguments("base_serv_fee")
        base_fee_template = []
        base_num = 0
        for base_name in base_serv_names:
            base_fee = base_serv_fees[base_num]
            # 价格转换成分
            base_fee = int(float(base_fee) * 100)
            base_fee_id = str(uuid.uuid1()).replace('-', '')
            base_json = {'_id':base_fee_id, 'name':base_name, 'fee':base_fee}
            base_fee_template.append(base_json)
            base_num = base_num + 1

        # 生成附加服务
        ext_serv_names = self.get_arguments("ext_serv_name")
        ext_serv_fees = self.get_arguments("ext_serv_fee")
        ext_fee_template = []
        ext_num = 0
        for ext_name in ext_serv_names:
            ext_fee = ext_serv_fees[ext_num]
            # 价格转换成分
            ext_fee = int(float(ext_fee) * 100)
            ext_fee_id = str(uuid.uuid1()).replace('-', '')
            ext_json = {'_id':ext_fee_id, 'name':ext_name, 'fee':ext_fee}
            ext_fee_template.append(ext_json)
            ext_num = ext_num + 1

        json = {"_id":activity_id, "ext_fee_template":ext_fee_template, "base_fee_template":base_fee_template}
        activity_dao.activity_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step8')


class VendorActivityDetailStep9Handler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity = self.get_activity(activity_id)
        # activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        counter = self.get_counter(vendor_id)
        activity_counter = self.get_counter(activity_id)
        self.render('vendor/activity-edit-step9.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter, activity_counter=activity_counter,
                activity=activity, categorys=categorys,
                bonus=bonus,
                cret_template=cret_template)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_notes = self.get_argument("notes", "")
        json = {"_id":activity_id, "notes":activity_notes}
        activity_dao.activity_dao().update(json);

        self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step9')


class VendorActivityActionPublishHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        access_token = self.get_secure_cookie("access_token")
        # ops = self.get_ops_info()

        activity = activity_dao.activity_dao().query(activity_id)
        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        applys = apply_dao.apply_dao().query_by_activity(activity_id)
        orders = order_dao.order_dao().query_by_activity(activity_id)
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)
        bonus = int(bonus_template['activity_shared']) + int(bonus_template['cret_shared'])
        qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)

        # 发布时判断一下是否已经填写费用信息
        activity = activity_dao.activity_dao().query(activity_id)

        if activity['base_fee_template']:
            activity_dao.activity_dao().update_status(activity_id, ACTIVITY_STATUS_RECRUIT)

            ids = {'ids':['0bbf89e2f73411e69a3c00163e023e51']}
            self.update_article_categories(activity_id, ids)
            self.publish_article(activity_id)

            self.redirect('/vendors/' + vendor_id + '/activitys/draft')
        else:
            self.redirect('/vendors/' + vendor_id + '/activitys/' + activity_id + '/detail/step8')



class VendorActivityActionDeleteHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_dao.activity_dao().delete(activity_id)
        self.redirect('/vendors/' + vendor_id + '/activitys/draft')


class VendorActivityActionKickoffHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_dao.activity_dao().update_status(activity_id, ACTIVITY_STATUS_DOING)
        self.redirect('/vendors/' + vendor_id + '/activitys/recruit')


class VendorActivityActionCancelHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_dao.activity_dao().update_status(activity_id, ACTIVITY_STATUS_CANCELED)
        self.redirect('/vendors/' + vendor_id + '/activitys/recruit')


# 取消活动后，恢复到草稿箱
class VendorActivityActionResetHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_dao.activity_dao().update_status(activity_id, ACTIVITY_STATUS_DRAFT)
        # 取消后的活动不能在分享列表里
        activity_share_dao.activity_share_dao().delete_by_activity(activity_id)

        self.redirect('/vendors/' + vendor_id + '/activitys/draft')


class VendorActivityActionPopularHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        json = {"_id":activity_id, "popular":True}
        activity_dao.activity_dao().update(json)
        self.redirect('/vendors/' + vendor_id + '/activitys/recruit')


class VendorActivityActionUnpopularHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        json = {"_id":activity_id, "popular":False}
        activity_dao.activity_dao().update(json)
        self.redirect('/vendors/' + vendor_id + '/activitys/pop')


class VendorActivityActionCompleteHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        activity_dao.activity_dao().update_status(activity_id, ACTIVITY_STATUS_COMPLETED)

        # query cretificate template of activity
        _cert_template = cret_template_dao.cret_template_dao().query(activity_id)

        # query all orders of activity
        orders = order_dao.order_dao().query_by_activity(activity_id);
        _timestamp = time.time()
        for order in orders:
            if order['status'] == ORDER_STATUS_BF_APPLY:
                # create cretificate for every member
                _cret_id = str(uuid.uuid1()).replace('-', '')
                json = {"_id":_cret_id, "vendor_id":vendor_id,
                        "create_time":_timestamp, "review":False,
                        "activity_id":activity_id, "account_id":order['account_id'], "vendor_id":vendor_id,
                        "distance":_cert_template['distance'],
                        "hours":_cert_template['hours'], "height":_cert_template['height'],
                        "speed":_cert_template['speed'], "road_map_url":_cert_template['road_map_url'],
                        "contour_map_url":_cert_template['contour_map_url']}
                cret_dao.cret_dao().create(json)

                # 修改订单状态
                order_dao.order_dao().update({"_id":order['_id'],
                        "status":ORDER_STATUS_BF_DELIVER,
                        "last_update_time":_timestamp})

                # 修改个人信息－证书个数
                _customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, order['account_id'])
                try:
                    _customer_profile['crets']
                except:
                    _customer_profile['crets'] = 0
                crets_num = int(_customer_profile['crets']) + 1
                vendor_member_dao.vendor_member_dao().update({
                        "account_id":order['account_id'],
                        "vendor_id":vendor_id,
                        "crets":crets_num,
                        "last_update_time":_timestamp})

        self.redirect('/vendors/' + vendor_id + '/activitys/doing')


class VendorActivityActionCloneHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()

        activity = activity_dao.activity_dao().query(activity_id)
        article_id = activity['article_id']
        logging.info("got article_id %r", article_id)

        # create activity
        new_activity_id = str(uuid.uuid1()).replace('-', '')
        timestamp = time.time()
        _json = {"_id":new_activity_id, "vendor_id":vendor_id,
                "status":ACTIVITY_STATUS_DRAFT, "popular":False,
                "create_time":timestamp, "last_update_time":timestamp,
                "title":activity['title'],
                "bk_img_url":activity['bk_img_url'],
                "category":activity['category'],
                "triprouter":activity['triprouter'],
                "location":activity['location'],
                "hidden":False,"cash_only":False,
                "begin_time":timestamp, "end_time":timestamp, "apply_end_time":timestamp,
                "distance":activity['distance'],
                "strength":activity['strength'],
                "scenery":activity['scenery'],
                "road_info":activity['road_info'],
                "kickoff":activity['kickoff'],
                "base_fee_template":activity['base_fee_template'],
                "ext_fee_template":activity['ext_fee_template'],
                "notes":activity['notes'],
                "member_min":activity['member_min'],
                "member_max":activity['member_max']}
        activity_dao.activity_dao().create(_json)

        # create wechat qrcode
        group_qrcode = group_qrcode_dao.group_qrcode_dao().query(activity_id)
        _json = {"_id":new_activity_id,
                "create_time":timestamp, "last_update_time":timestamp,
                "qrcode_url":group_qrcode['qrcode_url'],"wx_qrcode_url":group_qrcode['wx_qrcode_url']}
        group_qrcode_dao.group_qrcode_dao().create(_json)

        # create blog article
        if activity.has_key('article_id'):
            # 先取出旧的article_id和内容
            _article_id = activity['article_id']
            url = API_DOMAIN + "/api/articles/" + _article_id
            http_client = HTTPClient()
            response = http_client.fetch(url, method="GET")
            logging.info("got response %r", response.body)
            data = json_decode(response.body)
            article = data['rs']
            _paragraphs = article['paragraphs']
            # 再创建一个新的article
            article = {'title':activity['title'], 'subtitle':activity['location'], 'img':activity['bk_img_url'],'paragraphs':_paragraphs}
            _json = json_encode(article)
            headers = {"Authorization":"Bearer "+access_token}
            url = API_DOMAIN + "/api/articles"
            http_client = HTTPClient()
            response = http_client.fetch(url, method="POST", headers=headers, body=_json)
            logging.info("got response %r", response.body)
            data = json_decode(response.body)
            article = data['rs']
            new_article_id = article['_id']

            activity_dao.activity_dao().update({'_id':new_activity_id, 'article_id':new_article_id})

        # create cretificate
        cret_template = cret_template_dao.cret_template_dao().query(activity_id)

        _json = {"_id":new_activity_id,
                "create_time":timestamp, "last_update_time":timestamp,
                "distance":cret_template['distance'],
                "hours":cret_template['hours'],
                "height":cret_template['height'],
                "slope_length":cret_template['slope_length'],
                "speed":cret_template['speed'],
                "road_map_url":cret_template['road_map_url'],
                "contour_map_url":cret_template['contour_map_url']}
        cret_template_dao.cret_template_dao().create(_json)

        # create bonus
        bonus_template = bonus_template_dao.bonus_template_dao().query(activity_id)

        _json = {"_id":new_activity_id,
                "create_time":timestamp, "last_update_time":timestamp,
                "activity_shared":bonus_template['activity_shared'],
                "cret_shared":bonus_template['cret_shared']}
        bonus_template_dao.bonus_template_dao().create(_json)

        self.redirect('/vendors/' + vendor_id + '/activitys/draft')

#/vendors/<string:vendor_id>/activitys/<string:activity_id>/action/evaluate
class VendorActivityActionEvalHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        categorys = category_dao.category_dao().query_by_vendor(vendor_id)
        activity = activity_dao.activity_dao().query(activity_id)
        activity_id = activity["_id"]
        counter = self.get_counter(vendor_id)
        self.render('vendor/activity-eval.html',
               vendor_id=vendor_id,
               ops=ops,
               counter=counter,
               activity_id=activity_id)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)

        ops = self.get_ops_info()

        _content = self.get_argument("content", "")
        _score = self.get_argument("score", "")
        if _score :
            _score = int(_score)
        else :
            _score = 0

        activity = activity_dao.activity_dao().query(activity_id)
        triprouter_id = activity['triprouter']

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

        self.redirect('/vendors/' + vendor_id + '/activitys/completed')
