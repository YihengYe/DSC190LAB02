#!/usr/bin/python
import os
import pymysql
import sys
import json
import requests
from flask import Flask, request
from datetime import date
from datetime import datetime
import time



connection = pymysql.connect(host='localhost',
                                user='iotdev',
                                password='iotdb190',
                                db='iotdb',
                                cursorclass=pymysql.cursors.DictCursor
                                )

cursor = connection.cursor()

def process_db():
	now = datetime.now()
	timeout='TIMEOUT'
	error='ERROR'
	ok='OK'
	warning='WARNING'
	print(now.strftime("%Y-%m-%d %H:%M:%S")," I'm checking for timeout")
	sql='SELECT DISTINCT mac FROM iotdb.devices WHERE groupID=3'
	cursor.execute(sql)
	devs=cursor.fetchall()
	for dev in devs:
		mac=dev['mac']
		sql_ok="UPDATE iotdb.devices SET status='{0}'\
			 WHERE now()< DATE_ADD(lastseen, INTERVAL 10 SECOND) AND mac='{1}' AND groupID=3 ".format(ok, mac)
		sql_warning="UPDATE iotdb.devices SET status='{0}'\
			 WHERE now()> DATE_ADD(lastseen, INTERVAL 10 SECOND) \
				 AND mac='{1}' AND groupID=3 AND now()< DATE_ADD(lastseen, INTERVAL 600 SECOND)".format(warning, mac)
		sql_timeout="UPDATE iotdb.devices SET status='{0}'\
			 WHERE now()> DATE_ADD(lastseen, INTERVAL 600 SECOND) AND mac='{1}' AND groupID=3 ".format(timeout, mac)
		cursor.execute(sql_ok)
		connection.commit()
		cursor.execute(sql_warning)
		connection.commit()
		cursor.execute(sql_timeout)
		cursor.commit()
		





#========== MAIN ===========

while True:
	process_db()
	time.sleep(5)

connection.close()

