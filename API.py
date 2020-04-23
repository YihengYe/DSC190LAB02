#!/usr/bin/python
import os
import pymysql
import sys
import json
import requests
from flask import Flask, request
from datetime import date
from datetime import datetime

#import cgitb
import cgi, cgitb
#cgitb.enable()
print("Content-Type: text/html")
print("")

print("DSC190 API")



#GET URL, see my example urls at bottom, we write four functions together
if os.environ['REQUEST_METHOD']=='GET':
    pass
else:
    print('only GET is supportted')
    sys.exit(0)
params = cgi.FieldStorage()
time=datetime.now()
time=time.strftime('%Y-%m-%d %H:%M:%S')

# connect DB in the server
connection = pymysql.connect(host='localhost',
                             user='iotdev',
                             password='iotdb190',
                             db='iotdb',
                             cursorclass=pymysql.cursors.DictCursor
                             )

cursor = connection.cursor()

if params['cmd'].value == "LIST":
    if "gid" not in params.keys():
        sql = "SELECT * FROM iotdb.devices"
    else:
        sql= "SELECT * FROM iotdb.devices WHERE groupID="+ params['gid'].value
    cursor.execute(sql)
    data = cursor.fetchall()
    for item in data:
       item['lastseen'] = str(item['lastseen'])
    data = str(data)
    data = data.replace("u\'", "\'")
    data = data.replace("\'", "\"")
    print('{"devices" : ')
    print(data)
    print('}')

if params['cmd'].value == "GROUPS":
    if "gid" not in params.keys():
        sql = "SELECT groupName,Student_1,Student_2 FROM iotdb.groups"
    else:
        sql= "SELECT groupName,Student_1,Student_2 FROM iotdb.groups WHERE groupID=" + params['gid'].value
    cursor.execute(sql)
    data = cursor.fetchall()
    data = str(data)
    data = data.replace("u\'", "\'")
    data = data.replace("\'", "\"")
    print('{"groups" : ')
    print(data)
    print('}')

if params['cmd'].value == 'REG':
    mac = params['mac'].value
    check_sql = "SELECT * FROM iotdb.devices WHERE iotdb.devices.mac = '%s'" % mac
    cursor.execute(check_sql)
    data=cursor.fetchall()
    # if the device is not registered
    if len(data)<1:
        divi_sql = "INSERT INTO iotdb.devices(mac, groupID, lastseen) \
                    VALUES('{0}', '{1}', '{2}')".format(mac,params['gid'].value, time)
    else:
        divi_sql="UPDATE iotdb.devices \
            SET lastseen='{0}', groupID='{1}' \
            WHERE mac='{2}'".format(time, params['gid'].value, mac) 
    try:
        cursor.execute(divi_sql)
        connection.commit()
        status='OK'
    except Exception as e:
        status='failed'
        print(e)
    result={}
    result['mac']=mac
    result['time']=time
    result['status']=status
    print(result)



if params['cmd'].value == 'LOG':
    mac = params['mac'].value
    sql = "INSERT INTO iotdb.testlogs(mac, ts, temp, hum) \
           VALUES('{0}', '{1}', '{2}', '{3}')".format(mac, time, params['t'].value, params['h'].value)
    try:
        cursor.execute(sql)
        connection.commit()
        status='OK'
    except Exception as e:
        print(e)
        status="failed"
    result={}
    result['timestamp']=time
    result['status']=status
    print(result)
    
cursor.close()
connection.close()

"""
examples: (All methods are GET)
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=LIST
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=LIST&gid=2211
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=GROUPS
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=GROUPS&gid=3
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=LOG&mac=11:22:33:44&t=10&h=10
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=REG&mac=22:33:44:55&gid=2211

"""
