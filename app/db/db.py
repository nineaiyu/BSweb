#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/9/3

import MySQLdb
from config import dbconfig

print dbconfig.cloud_host
def execCloudSQL(sqlstr,cloud_host,dbname):
    if sqlstr is None or sqlstr == "":
        return None


    conn = None
    try:
        conn = MySQLdb.connect(host=cloud_host, user=dbconfig.cloud_user, passwd=dbconfig.cloud_pwd,
                               db=dbname, port=dbconfig.cloud_port, charset=dbconfig.cloud_charset)
    except Exception as e:
        raise e
        return "mysql connet is error"

    try:
        cur = conn.cursor()
        cur.execute(sqlstr)
        result = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
    except Exception as e:
        #raise e
        return tuple("insert error")
    else:
        if len(result)==0:
            return result
            return "insert is ok"
        else:
            return result
