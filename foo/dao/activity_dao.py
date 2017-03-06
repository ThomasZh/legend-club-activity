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
from global_const import MONGO_HOST, MONGO_PORT, MONGO_USR, MONGO_PWD, \
        ACTIVITY_STATUS_COMPLETED, MONGO_DB


# activity options
class activity_dao(singleton):
    __activity_collection = None;

    def __init__(self):
        if self.__activity_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__activity_collection = db.activity;
        else:
            logging.info("activity_dao has inited......");


    def create(self, json):
        self.__activity_collection.insert(json);
        logging.info("create activity success......");


    def update_status(self, _id, status):
        self.__activity_collection.update({"_id":_id}, {"$set":{"status":status}});
        logging.info("update activity status success......");


    def update(self, json):
        _id = json["_id"];
        self.__activity_collection.update({"_id":_id},{"$set":json});
        logging.info("update activity success......");


    def delete(self, _id):
        self.__activity_collection.remove({"_id":_id});
        logging.info("delete activity success......");


    # 分页查询，包含隐藏的活动
    def query_pagination_by_status(self, vendor_id, status, before, limit):
        if before == 0:
            cursor = self.__activity_collection.find({
                    "vendor_id":vendor_id,
                    "status":status}).sort("create_time",-1).limit(limit);
        else:
            cursor = self.__activity_collection.find({
                    "vendor_id":vendor_id,
                    "status":status,
                    "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array


    # 查询结果，不包含隐藏的活动
    def query_not_hidden_pagination_by_status(self, vendor_id, status, before, limit):
        cursor = self.__activity_collection.find({
                "vendor_id":vendor_id,
                "status":status,
                "hidden":False,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_by_popular(self, vendor_id):
        cursor = self.__activity_collection.find({"vendor_id":vendor_id,"popular":True})
        array = []
        for i in cursor:
            array.append(i)
        return array


    def query(self, _id):
        cursor = self.__activity_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data


    def query_by_triprouter(self, trip_router_id):
        cursor = self.__activity_collection.find({"triprouter":trip_router_id})
        array = []
        for i in cursor:
            array.append(i)
        return array
