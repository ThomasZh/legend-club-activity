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

import logging
import pymongo
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
from comm import singleton
from global_const import MONGO_HOST, MONGO_PORT, MONGO_USR, MONGO_PWD, MONGO_DB


#vendor member options
# {'_id':'uuid', 'vendor_id':VENDOR_ID, 'account_id':'from_aplan', 'create_time':0,
#   'comment':'...',
#   'bonus':0, 'history_bonus':0,
#   'rank':0,
#   'tour_leader':False,
#   'distance':0}
class vendor_member_dao(singleton):
    __vendor_member_collection = None;

    def __init__(self):
        if self.__vendor_member_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__vendor_member_collection = db.vendor_member;
        else:
            logging.info("vendor_member_dao has inited......");


    def create(self, json):
        self.__vendor_member_collection.insert(json);
        logging.info("create vendor member success......");


    def update(self, json):
        vendor_id = json["vendor_id"];
        account_id = json["account_id"];
        self.__vendor_member_collection.update({
                "vendor_id":vendor_id,
                "account_id":account_id},{"$set":json});
        logging.info("update vendor member success......");


    def query_pagination(self, vendor_id, before, limit):
        if before == 0:
            cursor = self.__vendor_member_collection.find({
                    "vendor_id":vendor_id,}).sort("create_time",-1).limit(limit);
        else:
            cursor = self.__vendor_member_collection.find({
                    "vendor_id":vendor_id,
                    "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array


    def query_not_safe(self, vendor_id, account_id):
        cursor = self.__vendor_member_collection.find({
                "vendor_id":vendor_id,
                "account_id":account_id})
        data = None
        for i in cursor:
            data = i
        return data


    def query(self, vendor_id, account_id):
        data = self.query_not_safe(vendor_id, account_id)
        if not data:
            logging.debug("data is None");
            data = {'_id':'00000000000000000000000000000000',
                    'vendor_id':vendor_id,
                    'account_id':account_id,
                    'account_nickname':'',
                    'account_avatar':'',
                    'comment':'',
                    'bonus':0,
                    'history_bonus':0,
                    'vouchers':0,
                    'distance':0,
                    'rank':0,
                    'crets':0}
            return data
        else:
            try:
                data['account_nickname']
            except:
                data['account_nickname'] = ''
            try:
                data['account_avatar']
            except:
                data['account_avatar'] = ''
            try:
                data['comment']
            except:
                data['comment'] = ''
            try:
                data['bonus']
            except:
                data['bonus'] = 0
            try:
                data['history_bonus']
            except:
                data['history_bonus'] = 0
            try:
                data['vouchers']
            except:
                data['vouchers'] = 0
            try:
                data['distance']
            except:
                data['distance'] = 0
            try:
                data['rank']
            except:
                data['rank'] = 0
            try:
                data['crets']
            except:
                data['crets'] = 0

            return data

    def query_by_keys(self, vendor_id, keys_value):
        cursor = self.__vendor_member_collection.find({
                "vendor_id":vendor_id,
                "account_nickname":{'$regex':keys_value}})
        array = []
        for i in cursor:
            array.append(i)
        return array
