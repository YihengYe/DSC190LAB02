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
#cgitb.enable()

print("Content-Type: text/html")
print("")

print("DSC190 API")


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


#POST interface
params = json.load(sys.stdin)
#params = json.loads('{"cmd":"LIST"}')

print('got this: ')
print(json.dumps(params))


connection = pymysql.connect(host='localhost',
                             user='iotdev',
                             password='iotdb190',
                             db='iotdb',
                             cursorclass=pymysql.cursors.DictCursor
                             )

cursor = connection.cursor()

if params['cmd'] == "LIST":
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

if params['cmd'] == "GROUPS":
    sql = "SELECT groupName,Student_1,Student_2 FROM groups"
    cursor.execute(sql)
    data = cursor.fetchall()
    data = str(data)
    data = data.replace("u\'", "\'")
    data = data.replace("\'", "\"")
    print('{"groups" : ')
    print(data)
    print('}')

cursor.close()
connection.close()
