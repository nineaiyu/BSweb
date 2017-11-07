#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/11/1

from sqlalchemy import *
from config import DevelopmentConfig
from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, Column, Integer, String
from sqlalchemy.orm import mapper, sessionmaker
'''
由于数据量比较小，用sqlite比较方便
'''
engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)

metadata = MetaData()


downuri = Table('downuri',metadata,
              Column('id',Integer, primary_key=True, autoincrement=True),
              Column('sitename',String(50), unique=True),
              Column('uri',String(600)),
              Column('description',String(10240)),
              Column('hostip',String(50)),
              Column('clientip',String(50)),
              Column('filetime',String(50)),
              Column('ispost',String(10)),
              Column('addtime',String(10)),
              Column('checkdata', String(10)),
              Column('datasize', String(20)))


class Downuri(object):
    def __init__(self, sitename,uri,description,hostip,clientip,filetime,ispost,addtime,checkdata,datasize):
        # self.id = id
        self.sitename = sitename
        self.uri = uri
        self.description = description
        self.hostip = hostip
        self.clientip = clientip
        self.filetime = filetime
        self.ispost = ispost
        self.addtime = addtime
        self.checkdata = checkdata
        self.datasize = datasize

mapper(Downuri, downuri)



restorejob = Table('restorejob',metadata,
              Column('id',Integer, primary_key=True, autoincrement=True),
              Column('clientip',String(50), unique=True),
              Column('hostip',String(600)),
              Column('sitename',String(10240)),
              Column('jobid',String(50)),
              Column('addtime',String(50)),
              Column('filetime',String(50)),
             )


class Restorejob(object):
    def __init__(self, clientip,hostip,sitename,jobid,addtime,filetime):
        # self.id = id
        self.sitename = sitename
        self.jobid = jobid
        self.hostip = hostip
        self.clientip = clientip
        self.addtime = addtime
        self.filetime = filetime

mapper(Restorejob, restorejob)



class Quary(object):
    Session_class = sessionmaker(bind=engine)
    Session = Session_class()
    def all(self,*args,**kwargs):
        return self.Session.query(*args).filter_by(**kwargs).order_by(desc('id')).all()
    def first(self,*args,**kwargs):
        return self.Session.query(*args).filter_by(**kwargs).first()


class Quarynodesc(object):
    Session_class = sessionmaker(bind=engine)
    Session = Session_class()
    def all(self,*args,**kwargs):
        return self.Session.query(*args).filter_by(**kwargs).order_by().all()
    def first(self,*args,**kwargs):
        return self.Session.query(*args).filter_by(**kwargs).first()


class Quarylike(object):
    Session_class = sessionmaker(bind=engine)
    Session = Session_class()
    def all(self,args,filter,state,limit):
        return (self.Session.query(args).filter(filter).filter(state).limit(limit).all())
    def first(self,args,filter,state,limit):
        return self.Session.query(args).filter(filter).filter(state).limit(limit).first()


class Insert(object):
    Session_class = sessionmaker(bind=engine)
    Session = Session_class()
    def insert(self,*args):
        self.Session.add(*args)
    def commit(self):
        self.Session.commit()

class Modify(object):
    Session_class = sessionmaker(bind=engine)
    Session = Session_class()
    def get(self,*args,**kwargs):
        ks = self.Session.query(*args).filter_by(**kwargs).all()
        return ks
    def commit(self):
        self.Session.commit()

class Delete(object):
    Session_class = sessionmaker(bind=engine)
    Session = Session_class()
    def delete(self,*args,**kwargs):
        ks = self.Session.query(*args).filter_by(**kwargs).all()
        for i in ks:
            self.Session.delete(i)
    def commit(self):
        self.Session.commit()

#
#
# def modify():
#     Hosts = Downuri
#     hostss = Modify()
#     hosts = hostss.get(Hosts,id='5')
#     for i in hosts:
#         print i.id, i.hostip ,i.type
#         i.hostip="999ee9"
#     hostss.commit()
# def delete():
#     Hosts = Downuri
#     hostss = Delete()
#     hostss.delete(Hosts,id=5)
#     hostss.commit()
# def insert(hostip):
#     print hostip
#     Hosts = Downuri(hostip=hostip,gateway='10.113.64.1',netype='bip')
#     hostss = Insert()
#     hostss.insert(Hosts)
#     hostss.commit()
# def select():
#     Hosts = Downuri
#     hostss = Quary()
#     hostsa = hostss.all(Hosts,type='pcnode')
#     for hosts in hostsa:
#         print hosts.id,hosts.hostip




