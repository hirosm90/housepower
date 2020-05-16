#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import sys
import queue
from keilib.worker import Worker
from influxdb import InfluxDBClient
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)

class InfluxDbWriter ( Worker ):
    def __init__( self , record_que, db_addr, db_port, db_user, db_pw, db_name, location_id):
        super().__init__()
        self.record_que = record_que
        self.location_id = location_id
        self.client = InfluxDBClient(host=db_addr, port=db_port, username=db_user, password=db_pw, database=db_name, timeout=3)
 
    def run ( self ):
        logger.info('[START]')
        while not self.stopEvent.is_set():
            try:
                filename, key, value, nazo = self.record_que.get(timeout=3)
            except:
                continue

            record = [
                {
                    "fields" : {
                        "inst_power" : float(value),
                    },
                    "tags" : {
                        "location" : self.location_id,
                        "req_type" : key,
                    },
                    "measurement" : "power"
                }
            ]
            logger.debug(record )
            try:
                ret=self.client.write_points(record)
                if ret:
                    pass
                else:
                    logger.warning("Error writing to Influx DB (return code): "+record)
                    self.stopEvent.set()
            except:
                logger.warning('Error writing to Infux DB (expcetion): '+record)
                self.stopEvent.set()

        logger.info('[STOP]')