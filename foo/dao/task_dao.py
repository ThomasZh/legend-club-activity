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


# task options
class task_dao(singleton):
    _task_collection = None;

    def __init__(self):
        if self._task_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self._task_collection = db.task;
        else:
            logging.info("task_dao has inited......");


    def create(self, json):
        self._task_collection.insert(json);
        logging.info("create task success......");


    def update(self, json):
        _id = json["_id"];
        self._task_collection.update({"_id":_id},{"$set":json});
        logging.info("update task success......");


    def delete(self, _id):
        self._task_collection.remove({"_id":_id});
        logging.info("delete task success......");


    def query(self, _id):
        cursor = self._task_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data

    def query_by_vendor(self, vendor_id):
        cursor = self._task_collection.find({"vendor_id":vendor_id})
        array = []
        for i in cursor:
            array.append(i)
        return array
