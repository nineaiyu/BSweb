#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/8/28
import json,urllib2,base64
from config import hosts
import datetime,time

from app.db import sqliteutil
import apiutils

hosts = hosts.hosts
auth = base64.b64encode('Nineven' + ':' + 'ZZidcNineven@0123')
headers = {"Authorization": "Basic " + auth}


def getrestoretime(clientip,hosts,sitename):
    joblists = []
    hostip="0.0.0.0"
    flag = 0
    for i in hosts:
        infos = json.loads(apiutils.getbacularestorelistsformysql(i,clientip))
        print infos
        if 'getjobtimes' not in str(infos):
            joblists.append('not found ,please check it')
        else:
            infos = infos["getjobtimes"]
            if len(infos) > 0 :
                hostip = i
                flag +=1
    if flag == 0:
        print("没有发现备份，请检查")
        joblists.append('not found ,please check it')
    elif flag ==1:
        checksite = json.loads(apiutils.checksiteinbacula(hostip,clientip,sitename))
        print 'checksite',checksite
        print type(checksite)
        if checksite['count'] == '0':
            return "notfound",hostip
        infos = json.loads(apiutils.getbacularestorelistsformysql(hostip,clientip))
        joblists = infos["getjobtimes"]
        while 'D' == joblists[len(joblists) -1]["LEVEL"]:
            joblists.pop()
    else:
        joblists.append('system error')
    return joblists,hostip

def rawinput(clientip,sitename):
    clientip = clientip[0]
    joblists,hostip = getrestoretime(clientip, hosts,sitename)
    count = 0
    print "备份服务器的ip：%s" %hostip
    if hostip == "0.0.0.0":
        return "999"
    if str(joblists) == "notfound":
        return "888#"+hostip
    jobinfo=""
    for j in joblists:
        count += 1
        if j == "system error":
            return "error"
        print "%d : %s" % (count, j)
        jobinfo += str(count)+"#"+str(j["startime"].replace("+",' '))+"#"+str(j["endtime"].replace("+",' '))+"#"+sitename+"#"+clientip+"#"+hostip+"<br/>"
    return jobinfo


def runrestores(options,sitename,ip):
    options = int(options)
    joblists, hostip = getrestoretime(ip, hosts,sitename)
    print options,hostip,joblists
    if joblists[options - 1]["LEVEL"] == "F":
        jobid = str(joblists[options - 1]["Jobid"])
        startime = str(joblists[options-1]["startime"])
    else:
        counts = options
        while counts < len(joblists):
            if 'F' == joblists[counts - 1]["LEVEL"]:
                break
            counts += 1
        jobid = str(joblists[counts - 1]["Jobid"]) + "," + str(joblists[options - 1]["Jobid"])
        startime = str(joblists[options - 1]["startime"]).replace('+',' ')
    print ip,jobid,sitename,hostip

    # checkbacularun = eval(apiutils.checkbaculaclient(hostip,ip))
    # if checkbacularun['code'] == "88":
    #     infos = apiutils.posturls(ip, jobid, sitename, hostip)
    #     Downloaduri = sqliteutil.Downuri(sitename=sitename, uri='http://127.0.0.1/files/download/hello',
    #                                      description=u'已经加入任务队列', hostip=hostip,
    #                                      clientip=ip, filetime=startime, ispost='no',
    #                                      addtime=str(datetime.datetime.now()).split('.')[0], checkdata='no')
    #     sqlitein = sqliteutil.Insert()
    #     sqlitein.insert(Downloaduri)
    #     sqlitein.commit()
    # else:
    Restorejobname = sqliteutil.Restorejob(clientip=ip, hostip=hostip, sitename=sitename,
                                           jobid=jobid, addtime=str(datetime.datetime.now()).split('.')[0],
                                           filetime=startime)
    sqlitein = sqliteutil.Insert()
    sqlitein.insert(Restorejobname)
    sqlitein.commit()
    return {"sitename": sitename,"hostip": hostip,'clientip':ip}


def runclientrestores(clientip,hostip):
    options = 1
    sitename = '\*'
    joblists ,cip= getrestoretime(clientip, hostip,'vhost')
    print joblists
    print cip
    if cip == "0.0.0.0":
        return "{\"code\":2,\"infos\":\"not found\"}"
    if joblists[options - 1]["LEVEL"] == "F":
        jobid = str(joblists[options - 1]["Jobid"])
    else:
        counts = options
        while counts < len(joblists):
            if 'F' == joblists[counts - 1]["LEVEL"]:
                break
            counts += 1
        jobid = str(joblists[counts - 1]["Jobid"]) + "," + str(joblists[options - 1]["Jobid"])
    return apiutils.posturls(clientip, jobid, sitename, cip)


def getdownuri():

    Downloaduri = sqliteutil.Downuri
    sqlitein = sqliteutil.Quary()
    infos = sqlitein.all(Downloaduri)
    urilists=[]
    uri={}
    for downuri in infos:
        uri["sitename"] = downuri.sitename
        uri["uri"] = downuri.uri
        uri["description"] = downuri.description
        uri["hostip"] = downuri.hostip
        uri["clientip"] = downuri.clientip
        uri["filetime"] = str(downuri.filetime).replace('+',' ')
        uri["ispost"] = downuri.ispost
        uri["addtime"] = downuri.addtime
        uri["checkdata"]= downuri.checkdata
        uri["datasize"] = downuri.datasize
        urilists.append(uri.copy())

    return urilists



def aveagetimes(timelists):
    allseconds = 0
    for ontime in timelists:
        print type(ontime)
        print 'ontime:',ontime
        i = ontime.split(',')
        if len(i) == 2 :
            days = int(i[0].split(' ')[0])
            oldhours = int(i[1].split(':')[0])
            ms = i[1].split(':')[1:]
            hours = days * 24 + oldhours
            estimes = str(hours)+':'+':'.join(ms)
        else:
            estimes = i[0]
        print 'estimes:',estimes
        allseconds+=ISOString2Time(estimes)

    avesecode = allseconds // len(timelists)

    return avesecode


def ISOString2Time(s):
    slists = s.split(":")
    return int(slists[0]) * 3600 + int(slists[1]) * 60 + int(slists[2])


def Time2ISOString(iItv):
        h=iItv/3600
        sUp_h=iItv-3600*h
        m=sUp_h/60
        sUp_m=sUp_h-60*m
        s=sUp_m
        return ":".join(map(str,(h,m,s)))


def getimesaut(hostip,clientip):
    entimeinfos = apiutils.getbaculareport(hostip, clientip)
    print entimeinfos
    stimes = []
    count = 0
    for i in entimeinfos:
        if i['Type'] == 'R' or i['JobStatus'] != 'T':
            continue
        elapsedtime = str(i['elapsed'])
        count += 1
        stimes.append(elapsedtime)
        if count > 7:
            break
    avtimes = aveagetimes(stimes)
    stime = avtimes
    for i in entimeinfos:
        if i['Type'] in ('R') and i['JobStatus'] in ('R','F', 'S', 'M', 'm', 's', 'j', 'c', 'd', 't', 'p', 'C'):
            return u"有任务正在还原,请耐心等待"
        elif i['Type'] in ('B') and i['JobStatus'] in ('R','F', 'S', 'M', 'm', 's', 'j', 'c', 'd', 't', 'p', 'C'):
            startime = i['StartTime']
            dtstarttime = datetime.datetime.strptime(startime, "%Y-%m-%d %H:%M:%S")
            ktimes = str(datetime.datetime.now() - dtstarttime)
            stime = aveagetimes(ktimes.split('.')[0].split(' '))
            break
        else:
            return u"已经加入任务队列，稍后会自动还原"
    print '用的时间:', stime
    runtimes = stime

    endtime = avtimes - runtimes
    if endtime <= 0 :
        endtime = u"超出平均完成时间 %s ，现已用时间 %s ,完成时间未知" % (Time2ISOString(avtimes),stime)
    else:
        endtime = u"备份任务正在运行，运行平均完成时间 %s ，现已用时间 %s ,预计 %s 完成" % (Time2ISOString(avtimes),stime,Time2ISOString(endtime))
    return str(endtime)

def runbaculajobquee():
    Restorejobname = sqliteutil.Restorejob
    sqlitein = sqliteutil.Quarynodesc()
    infos = sqlitein.all(Restorejobname)
    for jobinfo in infos:
        hostip = jobinfo.hostip
        clientip = jobinfo.clientip
        sitename = jobinfo.sitename
        jobid = jobinfo.jobid
        startime = jobinfo.filetime
        addtime = jobinfo.addtime
        checkbacularun = eval(apiutils.checkbaculaclient(hostip,clientip))
        print checkbacularun
        if checkbacularun['code'] == "88":
            getallsites()
            infos = apiutils.posturls(clientip, jobid, sitename, hostip)
            Downloaduri = sqliteutil.Downuri(sitename=sitename, uri='http://127.0.0.1/files/download/hello',
                                             description=u'已经加入任务队列', hostip=hostip,
                                             clientip=clientip, filetime=startime, ispost='no',
                                             addtime=str(datetime.datetime.now()).split('.')[0], checkdata='no',datasize=u'未知')
            sqliteins = sqliteutil.Insert()
            sqliteins.insert(Downloaduri)
            sqliteins.commit()
            Restorejobs = sqliteutil.Restorejob
            sqliteinjobs = sqliteutil.Delete()
            sqliteinjobs.delete(Restorejobs, hostip=hostip, sitename=sitename, clientip=clientip, addtime=addtime)
            sqliteinjobs.commit()
            time.sleep(5)


def getbacuajobquee():
    Restorejobname = sqliteutil.Restorejob
    sqlitein = sqliteutil.Quary()
    infos = sqlitein.all(Restorejobname)
    urilists = []
    uri = {}
    for jobinfo in infos:
        uri["hostip"] = jobinfo.hostip
        uri["clientip"] = jobinfo.clientip
        uri["sitename"] = jobinfo.sitename
        uri["jobid"] = jobinfo.jobid
        uri["startime"] = str(jobinfo.filetime).replace('+',' ')
        uri["addtime"] = jobinfo.addtime
        uri["endtime"] = getimesaut(jobinfo.hostip, jobinfo.clientip)
        urilists.append(uri.copy())
    return urilists





def  checkpostdata(serverip,sitename,clientip,addtime,ispost):
    if ispost != "ok":
        Downloaduri = sqliteutil.Downuri
        sqlitein = sqliteutil.Modify()
        infos = sqlitein.get(Downloaduri, hostip=serverip, sitename=sitename, clientip=clientip, addtime=addtime)
        for i in infos:
            i.checkdata = 'yes'
            i.description = u'数据压缩传输中'
            i.ispost = 'compressing'
        sqlitein.commit()
        datasize = u"未知"
        urinfos = eval(apiutils.getdownuris(serverip, sitename, clientip))
        print 'code', urinfos["code"]
        if str(urinfos["code"]) == '99':
            uri = 'http://127.0.0.1/files/download/hello'
            description = u"数据正在还原中"
            state = 'running'
            checkdata = 'no'
        elif   str(urinfos["code"]) == '33':
            uri = 'http://127.0.0.1/files/download/hello'
            description = u"通信异常"
            state = 'connect failed'
            checkdata = 'no'
        else:
            if str(urinfos["code"]) != '0':
                uri = 'http://127.0.0.1/files/download/hello'
                description = u"文件找不到"
                state = 'no'
                checkdata = 'yes'
            else:
                uri = urinfos["uri"]
                description = u"还原成功"
                datasize = urinfos["size"]
                state = 'ok'
                checkdata = 'yes'
        Downloaduri = sqliteutil.Downuri
        sqlitein = sqliteutil.Modify()
        infos = sqlitein.get(Downloaduri, hostip=serverip, sitename=sitename, clientip=clientip, addtime=addtime)
        for i in infos:
            print 'post', i.ispost
            if i.ispost != "ok":
                i.uri = uri
                i.ispost = state
                i.description = description
                i.checkdata = checkdata
                i.datasize = datasize
        sqlitein.commit()

def getallsites():
    infolists = getdownuri()
    for i in infolists:
        if i !=None :
            hostip=i["hostip"]
            sitename=i["sitename"]
            clientip=i["clientip"]
            addtime=i["addtime"]
            ispost=i["ispost"]
            ischeck=i["checkdata"]
            if ischeck == "yes":
                continue
            print hostip, sitename, clientip, addtime, ispost
            checkpostdata(hostip, sitename, clientip, addtime, ispost)

#print getrestoretime('10.112.0.193','10.112.0.200','HA333220')
#print getdownuri()


# Downloaduri = sqliteutil.Downuri
# sqlitein = sqliteutil.Modify()
# infos = sqlitein.get(Downloaduri,hostip='10.112.0.200',sitename='vhost',clientip='10.112.0.193',addtime='2017-11-01 19:36:02')
# for i in infos:
#     i.uri = 'A3ZWQ5Zjk1YTdjODdjM2MwODBmYzczMGQwNzcyMDgxOTNlYTU1YTFhOWY4YzJhN2RlMzhlZmYwM2FlMWVjNzI5NDgzMjgxMWViYmMzNmZlNzk0ZWRjNTIyN2FiYTA1OTI4YTJlOGNiZTU1YzRiMjU5NTk1OGE5YzBkMmY3ODAwYTY1ZGU4NGI0ODZjMzAwMDg5MGMwYTE4M2FiZjIyZWIzYjkwMzg2'
# sqlitein.commit()
