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


# club options
class club_dao(singleton):
    _club_collection = None;

    def __init__(self):
        if self._club_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self._club_collection = db.vendor_club;
        else:
            logging.info("club_dao has inited......");


    def create(self, json):
        self._club_collection.insert(json);
        logging.info("create club success......");


    def update(self, json):
        _id = json["_id"];
        self._club_collection.update({"_id":_id},{"$set":json});
        logging.info("update club success......");


    def delete(self, _id):
        self._club_collection.remove({"_id":_id});
        logging.info("delete club success......");

    # _id = vendor_id
    def query_not_safe(self, _id):
        cursor = self._club_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data


    # _id = vendor_id
    def query(self, _id):
        data = self.query_not_safe(_id)
        if not data:
            data = {"_id":_id, "club_name":"", "club_desc":"", "logo_img_url":"", "bk_img_url":""}
        else:
            try:
                data['club_name']
            except:
                data['club_name'] = ''
            try:
                data['club_desc']
            except:
                data['club_desc'] = ''
            try:
                data['logo_img_url']
            except:
                data['logo_img_url'] = ''
            try:
                data['bk_img_url']
            except:
                data['bk_img_url'] = ''

        return data
