#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/9/3

import os
import json,urllib2

def addbaculajob(serverip,clientip,systype,locate):

    args = {
        'key':"ImJmM2EyNGU5MWRkMTA1Yzc2YTNhOTEyMWYxOTFjY2FkZjU4ZDQyMTIi.DLeDsQ.1yuURBM3Y_wUF7d49CrxMh18l4s",
        'systype':systype,
        'locate': locate,
        'hostip':clientip
    }
    req_url = 'http://%s:9999/addbnserver' %serverip
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#print addbaculajob("10.220.209.222",'10.220.209.111','linux','HA')

def testsss():
    args = {
        "usrname":"HA900682",
        "path":"/www/users/HA900682/WEB",
        "function_name":"writesiteconfig",
        "siteconfig":"name",
    }
    req_url = 'http://10.112.0.193:5000/'
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url, data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res

def containsAny(allstr,childstr):
    for c in allstr:
        if c["Name"] == childstr:
            return 1
    return 0

# bcjob=[{u'Name': u'10.112.0.195-Backup', u'JobId': u'1'}, {u'Name': u'10.209.1.35-Backup', u'JobId': u'10'}, {u'Name': u'10.209.1.36-Backup', u'JobId': u'10'}, {u'Name': u'10.209.1.37-Backup', u'JobId': u'11'}, {u'Name': u'10.209.1.38-Backup', u'JobId': u'23'}, {u'Name': u'10.209.1.39-Backup', u'JobId': u'10'}, {u'Name': u'10.209.1.40-Backup', u'JobId': u'10'}, {u'Name': u'10.209.1.47-Backup', u'JobId': u'10'}, {u'Name': u'10.209.1.51-Backup', u'JobId': u'10'}, {u'Name': u'10.209.1.52-Backup', u'JobId': u'10'}, {u'Name': u'10.112.0.197-Backup', u'JobId': u'9'}]
# bcjobs=[]
# for i in bcjob:
#     bcjobs.append(i["Name"])
# confjobs=[]
# confjob=[{u'Name': u'10.112.0.195-Backup', u'JobId': u'1'}, {u'Name': u'10.209.1.35-Backup', u'JobId': u'10'}]
# for i in confjob:
#     confjobs.append(i["Name"])
#
# joblist=[]
# alljoblists = set(bcjobs).union(set(confjobs))
#
# togetherjobs=set(bcjobs).intersection(set(confjobs))
#
# troublejobs=set(bcjobs).symmetric_difference(set(confjobs))
#
# for i in togetherjobs:
#     joblist.append({"Name":i,"jobid":0})
# for i in troublejobs:
#     if containsAny(bcjob,i):
#         joblist.append({"Name": i, "jobid": 1})
#     if containsAny(confjob,i):
#         joblist.append({"Name": i, "jobid": -1})
# print joblist
# import time
# import datetime
# today = datetime.date.today()
# yesterday  =  today - datetime.timedelta(days=1)
# nowruntime = str(today) + " 22:00:00"
# runtime = datetime.datetime.strptime(nowruntime, '%Y-%m-%d %H:%M:%S')
# now = datetime.datetime.now()
# delta = now - runtime
# if delta.days < 1 and delta.days >= 0 :
#     yesterday=today
# #print str( today - datetime.timedelta(days=7))
#
# starttime="2017-10-19 17:51:48"
# endtime="2017-10-19 23:51:55"
# dtstarttime = datetime.datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
# dtendtime = datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
#
# print  int((dtendtime -dtstarttime).total_seconds())
#
# print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# k='dafsdf'
#
# print eval(k)
from app.db import sqliteutil

Downloaduri = sqliteutil.Downuri


sqlitein = sqliteutil.Quary()
info=sqlitein.first(Downloaduri,hostip='10.112.0.200',sitename='vhost',clientip='10.112.0.193',addtime='2017-11-01 20:37:20')
print info.uri
