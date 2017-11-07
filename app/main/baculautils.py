#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/9/3
import json
import apiutils
from config import hosts

hosts = hosts.hosts

def getrestorejob(host):
    jobs=json.loads(apiutils.getbacularestoreformysql(host))
    print jobs
    try:
        return jobs["restorejobs"]
    except:
        return {"info":"error"}

def getnewjobs(alljoblists,fjobs,wjobs,tjobs,rjobs):
    bcjobs=[]
    for i in fjobs:
        bcjobs.append(i)
    for i in wjobs:
        bcjobs.append(i)
    for i in tjobs:
        bcjobs.append(i)
    for i in rjobs:
        bcjobs.append(i)
    newjobs=[]
    for i in alljoblists["joblistsbcle"]["joblist"]:
        flag=0
        for j in bcjobs:
            if  i == j["Name"] :
                flag=1
                break
        if flag==0:
            if i in str(alljoblists["joblistsconf"]["joblist"]):
                newjobs.append(i)
    return newjobs

def containsAny(allstr,childstr):
    print allstr
    print childstr
    for c in allstr:
        if c == childstr:
            return 1
    return 0

def setjobs(alljoblists):

    joblist = []
    bcjobs = alljoblists["joblistsbcle"]["joblist"]
    confjobs= alljoblists["joblistsconf"]["joblist"]
    print 'confjobs',confjobs
    togetherjobs = set(bcjobs).intersection(set(confjobs))
    troublejobs = set(bcjobs).symmetric_difference(set(confjobs))

    for i in togetherjobs:
        joblist.append({"Name": i, "jobid": 0})
    for i in troublejobs:
        if containsAny(bcjobs, i):
            joblist.append({"Name": i, "jobid": 1})
        if containsAny(confjobs, i):
            joblist.append({"Name": i, "jobid": -1})
    print "joblists",joblist
    return joblist

def runfailjobs(alljoblists,fjobs,wjobs,tjobs,rjobs,tfjobs,runoverday,host,status):
    a=[]
    b=[]
    c=[]
    d=[]
    e=[]
    resultinfos={}
    newjobs=getnewjobs(alljoblists, fjobs, wjobs, tjobs, rjobs)
    nowjobs = len(tjobs)
    if nowjobs == len(alljoblists["joblistsbcle"]["joblist"]):
        statsinfo = "allok"
    else:
        statsinfo = "sumerunning"
    if len(fjobs) == 0:
        print "暂未发现失败任务"
    else:
        print "失败任务",fjobs
        print "运行任务",rjobs
        print "等待任务", wjobs
        print "成功任务", wjobs
        for j in fjobs:
            print "失败任务：" ,j
            if j["Name"] in str(tjobs):
                a.append(j)
            else:
                if j["Name"] in  str(rjobs) :
                    b.append(j)
                else:
                    if j["Name"] in str(wjobs):
                        c.append(j)
                    else:
                        if j["Name"] in str(tfjobs):
                           e.append(j)
                        else:
                            d.append(j)
                            print "调用脚本执行--%s" %j["Name"]
                            if status == 'run':
                                apiutils.runjobs(host, j["Name"])

    resultinfos["hostip"] = host
    resultinfos["jobstate"] = statsinfo
    resultinfos["countjobs"] = setjobs(alljoblists)
    resultinfos["successjobs"] = tjobs
    resultinfos["runningjobs"] = rjobs
    resultinfos["waitingjobs"] = wjobs
    resultinfos["failedjobs"] = fjobs
    resultinfos["failjobsuccess"] = a
    resultinfos["failjobrunning"] = b
    resultinfos["failjobwaiting"] = c
    resultinfos["failjobtorun"] = d
    resultinfos["failjoblimit"] = e
    resultinfos["jobslimitime"] = runoverday
    resultinfos["newjobs"] = newjobs

    print resultinfos
    return resultinfos

def checkallstatus(host,fjobs, wjobs, tjobs, rjobs,tfjobs,runoverday,alljoblists,status):
    return runfailjobs(alljoblists,fjobs, wjobs, tjobs, rjobs,tfjobs,runoverday,host,status)


def run(host,status):
    getbaculalist = json.loads(apiutils.getbaculajoblist(host))
    getmysqlinfo = json.loads(apiutils.getbaculafrommysql(host))
    print getmysqlinfo
    if getmysqlinfo.has_key('status'):
        return checkallstatus(host, [], [], [], [], [], [],
                              getbaculalist, status)
    failimitjobs = getmysqlinfo["failimitjobs"]
    failjobs = getmysqlinfo["failjobs"]
    runningjobs = getmysqlinfo["runningjobs"]
    runoveronedayjobs = getmysqlinfo["runoveronedayjobs"]
    successjobs = getmysqlinfo["successjobs"]
    waitingjobs = getmysqlinfo["waitingjobs"]
    return checkallstatus(host, failjobs, waitingjobs, successjobs, runningjobs, failimitjobs, runoveronedayjobs, getbaculalist,status)


def getrestorejobs():
    info = {'runjob':'None','hostip':'0.0.0.0'}
    infos = []
    print hosts
    for host in hosts:
        jobs = getrestorejob(host)
        if len(jobs) == 0:
            jobs = "0"
        info['runjob']=jobs
        info['hostip']=host
        infos.append(info.copy())
    print infos
    return infos

def start(status):
    infos = []
    for host in hosts:
        infos.append(run(host,status))
    return infos


