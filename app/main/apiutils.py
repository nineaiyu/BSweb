#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/10/4

import json,urllib2,base64
import xmltodict
import datetime
auth = base64.b64encode('Nineven' + ':' + 'ZZidcNineven@0123')
headers = {"Authorization": "Basic " + auth}

'''
定时任务，需要定时检查是否添加新的备份
'''
def checkbacula(serverip):
    args = {
        'state':'check'
    }
    req_url = 'http://%s:5000/vhost/api/v1/bacula/checkrunjobs' %serverip
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

#checkbacula("10.56.0.30")
'''
添加新的备份
'''
def addbaculajob(serverip,clientip,systype):
    '''
    :param serverip: 备份服务器的ip
    :param clientip: 要进行备份客户端的ip
    :param systype:  要进行备份客户端的系统 linux windows
    :return:
    '''
    args = {
        'host':clientip,
        'systype':systype
    }
    req_url = 'http://%s:5000/vhost/api/v1/bacula' %serverip
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

#addbaculajob("10.56.0.30","10.220.209.30","linux")

'''
删除备份
'''
def delbaculajob(serverip,clientip):
    req_url = 'http://%s:5000/vhost/api/v1/bacula/%s' % (serverip,clientip)
    req = urllib2.Request(url=req_url,headers=headers)
    req.get_method = lambda: 'DELETE'
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#delbaculajob("10.56.0.30","10.220.209.30")

'''
运行所有任务
'''
def runallbacula(serverip):
    args = {
        'jobname':'runalljobs'
    }
    req_url = 'http://%s:5000/vhost/api/v1/bacula/runjobs' %serverip
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#runallbacula("10.56.0.30")
##############################################################
''''''


'''
运行指定任务
'''
def runbaculajob(serverip,clientip):
    args = {
        'jobname':clientip
    }
    req_url = 'http://%s:5000/vhost/api/v1/bacula/runjobs' %serverip
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res





'''
增加nagios监控
'''

def addnagios(serverip,clientip,systype):
    if systype == "linux":
        systypeint=1
        netindex = 2
    elif systype == "windows":
        systypeint=2
        netindex = 13
    else:
        systypeint = 1
        netindex = 2
    args = {
        'host':clientip,
        'netindex':str(netindex),
        'systype':str(systypeint),
        'countrytype':'HA',
        'destription':'国内Linux虚拟主机'
    }

    req_url = 'http://%s:5000/vhost/api/v1/nagios' %serverip

    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#print addnagios("10.56.0.30","10.220.209.44",'linux')

'''
获取nagios信息
'''

'''
删除nagios
'''
def nagiosdelete(serverip,clientip):
    req_url = 'http://%s:5000/vhost/api/v1/nagios/%s' % (serverip, clientip)
    req = urllib2.Request(url=req_url,headers=headers)
    req.get_method = lambda: 'DELETE'
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#nagiosdelete("10.56.0.30","10.220.209.31")

'''
重载nagios，用于删除之后重载
'''

def reloadnagios(serverip):
    args = {
        'action':'reload'
    }
    req_url = 'http://%s:5000/vhost/api/v1/nagios/reloads' %serverip
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#reloadnagios("10.56.0.30")

'''
获取nagios信息
'''

def getnagios(serverip,clientip):
    '''

    :param serverip: 监控服务器的ip
    :param clientip:  客户端的ip，all
    :return:
    '''
    req_url = 'http://%s:5000/vhost/api/v1/nagios/%s' %(serverip,clientip)
    req = urllib2.Request(url=req_url,headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#getnagios("10.56.0.30","10.220.209.42")

'''
获取备份信息
'''
def getbacula(serverip,clientip):
    '''
    :param serverip: 备份服务端的ip
    :param clientip: 客户端的ip，all
    :return:
    '''
    req_url = 'http://%s:5000/vhost/api/v1/bacula/%s' %(serverip,clientip)
    req = urllib2.Request(url=req_url,headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#print getbacula("10.56.0.30","all")

'''
通过数据库获取备份信息
'''
def getbaculafrommysql(serverip):
    '''
    :param serverip: 备份服务端的ip
    :param clientip: 客户端的ip，all
    :return:
    '''
    req_url = 'http://%s:5000/vhost/api/v1/bacula/getbaculajobs' % serverip
    req = urllib2.Request(url=req_url,headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
#print getbaculafrommysql('10.56.0.30')

def getbacularestoreformysql(serverip):
    req_url = 'http://%s:5000/vhost/api/v1/bacula/getbacularestorejobs' % serverip
    req = urllib2.Request(url=req_url,headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res



def getbaculajoblist(serverip):
    req_url = 'http://%s:5000/vhost/api/v1/bacula/getbaculajoblist' % serverip
    req = urllib2.Request(url=req_url,headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

def sendmailreport(serverip):
    req_url = 'http://%s:9999/api/report/bacula/mail' %(serverip)
    req = urllib2.Request(url=req_url)
    try:
        res_data = urllib2.urlopen(req)
        res = res_data.read()
    except:
        res = {'code':12}
    return res


def getbacularestorelistsformysql(serverip,clientip):
    args = {
        'clientip':clientip
    }
    j_data = json.dumps(args)
    req_url = 'http://%s:5000/vhost/api/v1/bacula/getbacularestorejobslists' % serverip
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

def getbaculalogs(serverip,clientip,jobid):
    print serverip
    print clientip
    args = {
        'clientip':clientip,
        'jobid':jobid
    }
    j_data = json.dumps(args)
    req_url = 'http://%s:5000/vhost/api/v1/bacula/getjoblogs' % serverip
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    if len(res) == 0:
        return str({"info":"not found"})
    convertedDict = xmltodict.parse(res)
    jsonStr = json.dumps(convertedDict)
    #print "jsonStr=", jsonStr
    jsonStr = jsonStr.replace("@",'')
    return jsonStr.replace("\\n","<br/>")


def getbaculareport(serverip,clientip):
    args = {
        'clientip':clientip,
    }
    j_data = json.dumps(args)
    req_url = 'http://%s:5000/vhost/api/v1/bacula/getalljoblogs' % serverip
    req = urllib2.Request(url=req_url,headers=headers,data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    if len(res) == 0:
        return str({"info":"not found"})
    convertedDict = xmltodict.parse(res)
    jsonStr = json.dumps(convertedDict)
    jsonStr = jsonStr.replace("@",'')
    jobreports=[]
    jobreport = {}
    print jsonStr
    if 'row' not in str(jsonStr):
        jobreports=[]
    else:
        body = json.loads(jsonStr)
        data = body["resultset"]['row']
        for j in data:
            startime="2017-10-19 09:42:14"
            endtime="2017-10-19 09:42:14"
            if j == "field":
                m=data["field"]
            else:
                m=j["field"]
            for i in m:
                if i["name"] == "JobStatus":
                    jobreport["JobStatus"]=i["#text"]
                if i["name"] == "JobId":
                    jobreport["JobId"]=i["#text"]
                if i["name"] == "Level":
                    jobreport["Level"]=i["#text"]
                if i["name"] == "JobFiles":
                    jobreport["JobFiles"]=int(i["#text"])
                if i["name"] == "JobBytes":
                    jobreport["JobBytes"]=int(i["#text"])
                if i["name"] == "StartTime":
                    jobreport["StartTime"]=i["#text"]
                    if "0000-00-00 00:00:00"==i["#text"]:
                        startime="1972-01-01 01:01:01"
                    else:
                        startime=i["#text"]
                if i["name"] == "EndTime":
                    jobreport["EndTime"]=i["#text"]
                    if "0000-00-00 00:00:00"==i["#text"]:
                        endtime= str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        endtime = i["#text"]
                if i["name"] == "ReadBytes":
                    jobreport["ReadBytes"] = i["#text"]
                if i["name"] == "Type":
                    jobreport["Type"] = i["#text"]

                dtstarttime = datetime.datetime.strptime(startime, "%Y-%m-%d %H:%M:%S")
                dtendtime = datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
                jobreport["elapsed"] = dtendtime - dtstarttime
                jobreport["jobseconds"]=int((dtendtime - dtstarttime).total_seconds())
            jobreports.append(jobreport.copy())
            #jobreports.insert(0,jobreport.copy())
    jobreports.reverse()
    return jobreports

#print getbaculareport('10.112.0.200','10.112.0.197')


def runjobs(host, jobname):
    args = {'jobname': jobname}
    req_url = 'http://%s:5000/vhost/api/v1/bacula/runjobs' % host  # 10.214.0.3
    j_data = json.dumps(args)
    req = urllib2.Request(url=req_url, data=j_data, headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print json.loads(res)

def getalljobs(host):
    req_url = 'http://%s:5000/vhost/api/v1/bacula/sumjobs' % host  # 10.214.0.3
    req = urllib2.Request(url=req_url, headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return json.loads(res)['infos']['sumjobs']

def posturls(hostip,jobid,sitename,baculaip):
    args = {
        "hostip": hostip,
        "jobid": jobid,
        "path": "None",
        "sitename": sitename

    }
    req_url = 'http://%s:5000/vhost/api/v1/bacula/restorejobs' %baculaip

    j_data = json.dumps(args)
    print j_data
    print baculaip
    req = urllib2.Request(url=req_url, data=j_data,headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res


def checksiteinbacula(serverip, clientip,sitename):
    args = {
        'clientip': clientip,
        'sitename':sitename
    }
    j_data = json.dumps(args)
    req_url = 'http://%s:5000/vhost/api/v1/bacula/checksiteinbacula' % serverip
    req = urllib2.Request(url=req_url, headers=headers, data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

def checkbaculaclient(serverip, clientip):
    args = {
        'clientip': clientip,
    }
    j_data = json.dumps(args)
    req_url = 'http://%s:5000/vhost/api/v1/bacula/checkbaculaclient' % serverip
    req = urllib2.Request(url=req_url, headers=headers, data=j_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

def getdownuris(serverip, sitename,clientip):
    args = {
        'sitename': sitename,
        'clientip':clientip
    }
    j_data = json.dumps(args)
    req_url = 'http://%s:5000/vhost/api/v1/bacula/getdownuris' % serverip
    try:
        req = urllib2.Request(url=req_url, headers=headers, data=j_data)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
    except :
        res = str({"code":33,"info":"connect failed"})
    return res

def delflagfile(serverip, sitename, clientip):
    args = {
        'sitename': sitename,
        'clientip': clientip
    }
    j_data = json.dumps(args)
    req_url = 'http://%s:5000/vhost/api/v1/bacula/delflagfile' % serverip
    try:
        req = urllib2.Request(url=req_url, headers=headers, data=j_data)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
    except:
        res = str({"code": 33, "info": "connect failed"})
    return res


#print checksiteinbacula("10.112.0.200","10.112.0.199","liuyu")
# xmlStr=getbaculalogs("10.56.0.30",'10.112.0.166','3')
# print xmlStr.replace("\\n","<br/>")
# ks=json.loads(xmlStr)
# print "============================",ks
#
# infos = ks["resultset"]['row']
# for i in infos:
#     print i["field"][1],i["field"][2],i["field"][3]

#print addnagios("10.56.0.30","10.112.0.195","linux")
#print addbaculajob("10.112.0.200","10.112.0.20","linux")
#print nagiosdelete("10.112.0.200","10.112.0.192")
#print delbaculajob("10.112.0.200","10.112.0.20")
#print getbaculajoblist("10.56.0.30")
#print getallbaculalogs("10.56.0.30","10.209.1.38")

# print getbacularestorelistsformysql('10.112.0.200','10.112.0.193')

#print posturls('10.112.0.193', '22', 'HA20171034', '10.112.0.200')

#print getdownuris('10.112.0.200', 'vhost','10.112.0.193')
#print checkbaculaclient('10.112.0.200', '10.112.0.193')