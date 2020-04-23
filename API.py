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
import cgi
#cgitb.enable()

print("Content-Type: text/html")
print("")

print("DSC190 API")

"""
# GET interface
if(len(sys.argv) <= 1):
   print("no arg provided!")
   #sys.exit()

print(sys.argv)
print(sys.stdin)

params = {x.split("@")[0]:x.split("@")[1] for x in sys.argv[1].split("\\&")}

print(sys.argv)
param_len = len(sys.argv)
print("GET Len:",param_len)
"""


#POST interface
params = cgi.FieldStorage()
#params = json.loads('{"cmd":"LIST"}')

print('got this: ')
print(json.dumps(params))

# connect DB in the server
connection = pymysql.connect(host='localhost',
                             user='iotdev',
                             password='iotdb190',
                             db='iotdb',
                             cursorclass=pymysql.cursors.DictCursor
                             )

cursor = connection.cursor()

if params['cmd'].value == "LIST":
    sql = "SELECT * FROM devices"
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
    sql = "SELECT groupName,Student_1,Student_2 FROM groups"
    cursor.execute(sql)
    data = cursor.fetchall()
    data = str(data)
    data = data.replace("u\'", "\'")
    data = data.replace("\'", "\"")
    print('{"groups" : ')
    print(data)
    print('}')

if paramsp['cmd'].value == 'REG':
    mac = '22:22:33:55'
    sql = "SELECT * FROM iotdb.devices WHERE devices.mac = %s" % mac
    res = cursor.execute(sql)
    print(res)
    data = str(data)
    data = data.replace("u\'", "\'")
    data = data.replace("\'", "\"")
    print('{"reg" : ')
    print(data)
    print('}')

# if paramsp['cmd'].value == 'LOG':
#     mac = '22:22:33:55'
#     sql = "SELECT * FROM iotdb.devices WHERE devices.mac = %s" % mac
#     cursor.execute(sql)
#     data = str(data)
#     data = data.replace("u\'", "\'")
#     data = data.replace("\'", "\"")
#     print('{"reg" : ')
#     print(data)
#     print('}')

cursor.close()
connection.close()
