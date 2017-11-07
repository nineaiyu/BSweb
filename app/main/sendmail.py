#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/8/25

'''
smtp.exmail.qq.com
***
'''
import smtplib
from config import SendmailUser,Config
from email.mime.text import MIMEText

mailto_list = SendmailUser.mailto_list
mail_host = Config.MAIL_SERVER # 设置服务器
mail_user = Config.MAIL_USERNAME  # 用户名
mail_pass = Config.MAIL_PASSWORD  # 口令
mail_postfix = "qq.com"  # 发件箱的后缀


def send_mail(to_list, sub, content):
    me = '虚拟主机备份监控' + "<" + mail_user + ">"
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string(unicode))
        server.close()
        return True
    except Exception as e:
        print(str(e))
        return False


def send(infos):
    if send_mail(mailto_list, "备份报告", infos):
        print("发送成功")
    else:
        print("发送失败")


if __name__ == '__main__':
    if send_mail(mailto_list, "警告", "备份任务如下所示！"):
        print("发送成功")
    else:
        print("发送失败")























