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
	sql='SELECT DISTINCT blemac FROM iotdb.blelogs WHERE gid=3'
	cursor.excute(sql)
	devs=cursor.fetchall()
	for dev in devs:
		mac=dev['blemac']
		sql_timeout="UPDATE iotdb.devices SET status='{0}'\
			 WHERE now()> DATE_ADD(lastseen, INTERVAL 30 SECOND) AND mac='{1}' AND groupID=3 ".format(timeout, mac)
		sql_error=sql_timeout="UPDATE iotdb.devices SET status='{0}'\
			 WHERE now()> DATE_ADD(lastseen, INTERVAL 60 SECOND) \
				 AND mac='{1}' AND groupID=3 AND status='{2}'".format(error, mac, timeout)
		sql2="SELECT status FROM iotdb.devices WHERE groupID=3 AND mac='{0}'".format(mac)
		cursor.excute(sql2)
		st1=cursor.fetchall()[0]
		st=st1['status']
		if st==timeout or st==error:
			sql3="SELECT * FROM iotdb.blelogs WHERE gid=3 AND now()< DATE_ADD(timestamp, INTERVAL 15 SECOND)\
				AND mac='{0}'".format(mac)
			cursor.excute(sql3)
			data=cursor.fetchall()
			if len(data)>=1:
				sql_warning="UPDATE iotdb.devices SET status='{0}'\
			 		WHERE mac='{1}' AND groupID=3".format(warning, mac)
				cursor.excute(sql_warning)
				connection.commit()

		elif st==warning:
			sql4="SELECT * FROM iotdb.blelogs WHERE gid=3 AND now()< DATE_ADD(timestamp, INTERVAL 30 SECOND)\
				AND mac='{0}'".format(mac)
			cursor.excute(sql4)
			data=cursor.fetchall()
			if len(data)>=3:
				sql_ok="UPDATE iotdb.devices SET status='{0}'\
			 		WHERE mac='{1}' AND groupID=3".format(ok, mac)
				cursor.excute(sql_ok)
				connection.commit()
		else:
			cursor.excute(sql_timeout)
			connection.commit()
			cursor.excute(sql_error)
			connection.commit()





#========== MAIN ===========

while True:
	process_db()
	time.sleep(5)

connection.close()

