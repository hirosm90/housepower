#/usr/bin/python3
# -*- coding: utf-8 -*-

import queue
import configparser
import os
from keilib.broute   import BrouteReader, WiSunRL7023
from keilib.infulxdb import InfluxDbWriter


# settings for FileRecorder
record_que = queue.Queue(50)

# 設定ファイル読み込み
config_ini = configparser.ConfigParser()
config_ini_path = 'kei.ini'
config_ini.read(config_ini_path,encoding='utf-8')

# settings for BrouteReader
broute_port = config_ini['B-ROUTE']['Broute_Device']
broute_baudrate = 115200

wisundev = WiSunRL7023 (
                port=broute_port,
                baud=broute_baudrate,
                type=WiSunRL7023.IPS # Bルート専用タイプ
                # type=WiSunRL7023.DSS # デュアルスタックタイプ
            )

#
# B-Route ID, Pwd, Location
#
location_id = config_ini['B-ROUTE']['Location']
broute_id = config_ini['B-ROUTE']['Broute_ID']
broute_pwd = config_ini['B-ROUTE']['Broute_Password']

requests = [
    { 'epc':['D3','D7','E1'], 'cycle': 3600 },  # 係数(D3),有効桁数(D7),単位(E1),3600秒ごと
    { 'epc':['E7'], 'cycle': 10 },              # 瞬時電力(E7),10秒ごと
    { 'epc':['E0'], 'cycle': 300 },             # 積算電力量(E0),300秒ごと
]
# definition fo worker objects

worker_def = [
    {
        'class': InfluxDbWriter,
        'args': {
            'record_que': record_que,
            'db_addr': config_ini['InfluxDB']['Address'],
            'db_port': int(config_ini['InfluxDB']['Port']),
            'db_user': config_ini['InfluxDB']['User'],
            'db_pw': config_ini['InfluxDB']['Password'],
            'db_name': config_ini['InfluxDB']['DatabaseName'],
            'location_id': location_id,
        } 
    },
    {
        'class': BrouteReader,
        'args': {
            'wisundev': wisundev,
            'broute_id': broute_id,
            'broute_pwd': broute_pwd,
            'requests': requests,
            'record_que': record_que,
        }
    },
]
