#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/10/27
import forsafe
import base64
import datetime,time

def forsafes(strings,length):
    pc = forsafe.prpcrypt('i*am*a*smart*boy')
    e = pc.encrypt(strings,length)
    return e

def checktime(timestring,limithour):
    pc = forsafe.prpcrypt('i*am*a*smart*boy')
    timestrings = pc.decrypt(timestring)
    print timestrings
    if timestrings == 'error':
        return False
    if limithour == 0:
        return timestrings.split('@')[1]
    times = timestrings.split('@')[0]
    detimes = base64.b64decode(times)
    print detimes
    nowtime = datetime.datetime.now()
    print time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(detimes)))
    limitime = nowtime - datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(detimes))), '%Y-%m-%d %H:%M:%S')
    print limitime.seconds
    if limitime.seconds > limithour*3600:
        return False
    return True

ALLOWED_EXTENSIONS = set(['iso', 'rar', 'zip','gz'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
