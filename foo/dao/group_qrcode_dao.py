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


#group qrcode options
# {group_id, qrcode_url, create_time}
class group_qrcode_dao(singleton):
    __group_qrcode_collection = None;


    def __init__(self):
        if self.__group_qrcode_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__group_qrcode_collection = db.group_qrcode;
        else:
            logging.info("group_qrcode_dao has inited......");


    def create(self, json):
        self.__group_qrcode_collection.insert(json);
        logging.info("create group qrcode success......");


    # _id = group_id
    def query(self, _id):
        cursor = self.__group_qrcode_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data


    def update(self, json):
        _id = json["_id"];
        self.__group_qrcode_collection.update({"_id":_id},{"$set":json});
        logging.info("update group qrcode success......")
