#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/10/24
from app.main import apiutils
import datetime
clientip='10.112.0.193'
hostip='10.112.0.200'
entimeinfos = apiutils.getbaculareport(hostip,clientip)
print entimeinfos

for i in entimeinfos:
    for i in entimeinfos:
        if i['Type'] in ('B','R') and i['JobStatus'] in ('R','F', 'S', 'M', 'm', 's', 'j', 'c', 'd', 't', 'p', 'C'):
            startime = i['StartTime']
            print startime
            dtstarttime = datetime.datetime.strptime(startime, "%Y-%m-%d %H:%M:%S")
            stime = str(datetime.datetime.now() - dtstarttime).split('.')[0]
            print '用的时间:',stime
            print stime.split(' ')
            break


















