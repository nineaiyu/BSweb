#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/10/5

import config
import apiutils
import json

baculaip = config.BNserver.baculaip
nagiosip = config.BNserver.nagiosip

def getnagiosip(locate):
    bnip = {
        'bip': baculaip[0]['hostip'],
        'nip': nagiosip[0]['hostip'],
    }
    for i in baculaip:
        if i['locate'] == locate and i['state'] == 0:
            infos = json.loads(apiutils.getbacula(i["hostip"],'sumjobs'))
            sumcount = int(infos['infos']['sumjobs'])
            confcount = int(i['limit'])
            if sumcount >= confcount:
                continue
            else:
                bnip['bip'] = i["hostip"]
                break

    for i in nagiosip:
        if i['locate'] == locate  and i['state'] == 0:
            infos = json.loads(apiutils.getnagios(i["hostip"],'sum'))
            sumcount = int(infos['return_info']['sumjobs'])
            confcount = int(i['limit'])
            if sumcount >= confcount:
                continue
            else:
                bnip['nip'] = i["hostip"]
                break

    return bnip


