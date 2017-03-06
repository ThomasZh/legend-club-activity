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


#activity apply options
class apply_dao(singleton):
    __apply_collection = None;


    def __init__(self):
        if self.__apply_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__apply_collection = db.apply;
        else:
            logging.info("apply_dao has inited......");


    def create(self, json):
        self.__apply_collection.insert(json);
        logging.info("create apply success......");


    def query_by_activity(self, activity_id):
        cursor = self.__apply_collection.find({"activity_id":activity_id})
        array = []
        for i in cursor:
            array.append(i)
        return array


    def query_by_order(self, order_id):
        cursor = self.__apply_collection.find({"order_id":order_id})
        array = []
        for i in cursor:
            array.append(i)
        return array


    def query_pagination_by_vendor(self, vendor_id, before, limit):
        cursor = self.__apply_collection.find({
                "vendor_id":vendor_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array


    def count_not_review_by_vendor(self, vendor_id):
        return self.__apply_collection.count({
                "vendor_id":vendor_id,
                "review":False})


    # 查询活动参加人数，以此来计算活动执行状态
    # @2016/06/06
    def count_by_activity(self, activity_id):
        return self.__apply_collection.count({"activity_id":activity_id})


    def update(self, json):
        _id = json["_id"];
        self.__apply_collection.update({"_id":_id},{"$set":json});
        logging.info("update apply success......");

    def query_by_title_keys(self, vendor_id, title_keys_value):
        cursor = self.__apply_collection.find({
                "vendor_id":vendor_id,
                "activity_title":{'$regex':title_keys_value}}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_by_nickname_keys(self, vendor_id, nickname_keys_value):
        cursor = self.__apply_collection.find({
                "vendor_id":vendor_id,
                "account_nickname":{'$regex':nickname_keys_value}}).sort("create_time",-1)
                # "name":{'$regex':nickname_keys_value}})
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_by_time_keys(self, vendor_id, begin_keys_value, end_keys_value):
        cursor = self.__apply_collection.find({
                "vendor_id":vendor_id,
                "create_time":{'$gt':begin_keys_value,'$lt':end_keys_value}}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array
