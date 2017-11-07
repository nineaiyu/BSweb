#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/9/1
import apiutils
from config import BNserver
import logging
import baculamodels
logging.basicConfig()

"""
Demonstrates how to use the background scheduler to schedule a job that executes on 3 second
intervals.
"""

from datetime import datetime
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
import baculautils

def checbaculatick():
    print('Tick! The time is: %s' % datetime.now())
    serverip='localhost'
    apiutils.sendmailreport(serverip)

def runfailjob():
    baculautils.start("run")
    print("run fail job")

def checkpostdata():
    baculamodels.runbaculajobquee()
    time.sleep(1)
    baculamodels.getallsites()

def checkbacularestart():
    for i in BNserver.baculaip:
        if i["state"] == 0:
            apiutils.checkbacula(i["hostip"])

def runsc():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(tick, 'interval', seconds=3)
    # scheduler.add_job(tick, 'date', run_date='2016-02-14 15:01:05')
    #scheduler.add_job(tick, 'cron',minute='*/2')
    scheduler.add_job(checbaculatick, 'cron',day='*/1',hour='8,12,17')
    #scheduler.add_job(checbaculatick, 'cron',second='*/30')
    scheduler.add_job(checkbacularestart,'cron',minute='*/10')
    scheduler.add_job(checkpostdata, 'cron', second='*/30')
    scheduler.add_job(runfailjob, 'cron', day='*/1', hour='7,13')
    '''
        year (int|str) – 4-digit year
        month (int|str) – month (1-12)
        day (int|str) – day of the (1-31)
        week (int|str) – ISO week (1-53)
        day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour (int|str) – hour (0-23)
        minute (int|str) – minute (0-59)
        second (int|str) – second (0-59)

        start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
        end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
        timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)

        *    any    Fire on every value
        */a    any    Fire every a values, starting from the minimum
        a-b    any    Fire on any value within the a-b range (a must be smaller than b)
        a-b/c    any    Fire every c values within the a-b range
        xth y    day    Fire on the x -th occurrence of weekday y within the month
        last x    day    Fire on the last occurrence of weekday x within the month
        last    day    Fire on the last day within the month
        x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions
    '''
    scheduler.start()  # 这里的调度任务是独立的一个线程

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
     #   while True:
     #        time.sleep(2)  # 其他任务是独立的线程执行
             print('sleep!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
        print('Exit The Job!')

from threading import Thread
def dingshirenwu():
    thr = Thread(target=runsc)
    thr.start()
