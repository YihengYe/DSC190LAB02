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
	sql='SELECT * FROM iotdb.devices WHERE groupID=3'
	cursor.excute(sql)
	devs=cursor.fetchall()
	for dev in devs:
		mac=dev['mac']
		sql_timeout="UPDATE iotdb.devices SET status='{0}'\
			 WHERE mac='{1}' AND groupID=3 ".format(TIMEOUT, mac)




#========== MAIN ===========
while True:
	process_db()
	time.sleep(5)

connection.close()

