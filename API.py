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


def execute_sql(sql_cmd, cursor):
    cursor.execute(sql_cmd)
    res = cursor.fetchall()
    return res


def display_data(data, title = ''):
    data = str(data)
    data = data.replace("u\'", "\'")
    data = data.replace("\'", "\"")
    print('{"%s" : ' % title)
    print(data)
    print('}')


def format_result(fields, args):
    assert len(fields) == len(args), 'length mismatch!'

    result = {}
    for i in range(len(fields)):
        result[fields[i]] = args[i]
    
    print(result)


def get_global_time(time_format = '%Y-%m-%d %H:%M:%S'):
    out = datetime.now().strftime(time_format)
    return out


def get_list(params, cursor):
    if "gid" not in params.keys():
        sql = "SELECT * FROM iotdb.devices"
    else:
        sql= "SELECT * FROM iotdb.devices WHERE groupID=%s" % params['gid'].value

    data = execute_sql(sql, cursor)
    for item in data:
       item['lastseen'] = str(item['lastseen'])
    
    display_data(data, 'devices')


def get_groups(params, cursor):
    if 'gid' not in params.keys():
        sql = "SELECT groupName,Student_1,Student_2 FROM iotdb.groups"
    else:
        sql= "SELECT groupName,Student_1,Student_2 FROM iotdb.groups WHERE groupID=%s" % params['gid'].value
    data = execute_sql(sql, cursor)
    display_data(data, 'groups')
    

def get_reg(params, cursor):
    mac = params['mac'].value
    query = "SELECT * FROM iotdb.devices WHERE iotdb.devices.mac = '%s'" % mac
    data = execute_sql(query, cursor)

    # if the device is not registered, insert the new
    if len(data) < 1:
        divi_sql = "INSERT INTO iotdb.devices(mac, groupID, lastseen) \
                    VALUES('{0}', '{1}', '{2}')".format(mac, 
                    params['gid'].value, 
                    time)
    # if an existing device, update the origin
    else:
        divi_sql="UPDATE iotdb.devices \
            SET lastseen='{0}', groupID='{1}' \
            WHERE mac='{2}'".format(time,
             params['gid'].value, 
             mac) 
    try:
        execute_sql(divi_sql, cursor)
        connection.commit()
        status='successed'
        
    except Exception as err:
        status = 'failed'
        print(err)

    format_result(['mac', 'time', 'status'], [mac, time, status])


def get_log(params, cursor):
    mac = params['mac'].value
    temp = params['t'].value
    hum = params['h'].value

    sql = "INSERT INTO iotdb.testlogs(mac, ts, temp, hum) \
           VALUES('{0}', '{1}', '{2}', '{3}')".format(mac, time, temp, hum)
    try:
        execute_sql(sql, cursor)
        connection.commit()

        status='successed'
    except Exception as err:
        print(err)
        status="failed"

    format_result(['timestamp', 'status'], [time, status])

def post_reg(params, cursor):
    mac = params['mac']
    query = "SELECT * FROM iotdb.devices WHERE iotdb.devices.mac = '%s'" % mac
    data = execute_sql(query, cursor)

    # if the device is not registered, insert the new
    if len(data) < 1:
        divi_sql = "INSERT INTO iotdb.devices(mac, groupID, ip) \
                    VALUES('{0}', '{1}', '{2}')".format(mac, 
                    params['gid'], 
                    params['ip'])
    # if an existing device, update the origin
    else:
        divi_sql="UPDATE iotdb.devices \
            SET ip='{0}', groupID='{1}' \
            WHERE mac='{2}'".format(params['ip'],
             params['gid'], 
             mac) 
    try:
        execute_sql(divi_sql, cursor)
        connection.commit()
        status='successed'
        
    except Exception as err:
        status = 'failed'
        print(err)

    format_result(['mac', 'time', 'status'], [mac, time, status])

def post_logdev(params, cursor):
    mac = params['mac']
    query = "SELECT * FROM iotdb.devlogs WHERE iotdb.devlogs.mac = '%s'" % mac
    data = execute_sql(query, cursor)
    # if the device is not registered, insert the new
    if len(data) < 1:
        divi_sql = "INSERT INTO iotdb.devlogs(mac, groupID, RSSI) \
                    VALUES('{0}', '{1}', '{2}')".format(mac, 
                    params['gid'], 
                    params['RSSI'])
    # if an existing device, update the origin
    else:
        divi_sql="UPDATE iotdb.devlogs \
            SET RSSI='{0}', groupID='{1}' \
            WHERE mac='{2}'".format(params['RSSI'],
             params['gid'], 
             mac) 
    try:
        execute_sql(divi_sql, cursor)
        connection.commit()
        status='successed'
        
    except Exception as err:
        status = 'failed'
        print(err)

    format_result(['mac', 'time', 'status'], [mac, time, status])


def main():

    print("Content-Type: text/html")
    print("")
    print("DSC190 API version 0.0.3")

    #GET URL, see my example urls at bottom, we write four functions together
    if os.environ['REQUEST_METHOD']=='GET':
        ger=True
    elif os.environ['REQUEST_METHOD']=='POST':
        ger=False
    else:
        print('only GET and POST are supportted')
        sys.exit(0)
    if ger:
        params = cgi.FieldStorage()
    else:
        params=json.load(sys.stdin)
        print(json.dumps(params))
    # print(params.value)
    global time
    time = get_global_time()

    # connect DB in the server
    global connection
    connection = pymysql.connect(host='localhost',
                                user='iotdev',
                                password='iotdb190',
                                db='iotdb',
                                cursorclass=pymysql.cursors.DictCursor
                                )

    cursor = connection.cursor()
    if ger:
        if params['cmd'].value.upper() == 'LIST':
            get_list(params, cursor)

        if params['cmd'].value.upper() == 'GROUPS':
            get_groups(params, cursor)

        if params['cmd'].value.upper() == 'REG':
            get_reg(params, cursor)

        if params['cmd'].value.upper() == 'LOG':
            get_log(params, cursor)
    else:
        if params['cmd']=='REG':
            post_reg(params, cursor)
        if params['cmd']=='LOGDEV':
            post_logdev(params, cursor)

    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()

    
"""
examples: (All methods are GET)
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=LIST
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=LIST&gid=2211
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=GROUPS
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=GROUPS&gid=3
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=LOG&mac=11:22:33:44&t=10&h=10
http://dsc-iot.ucsd.edu/gid03/cgi-bin/API.py?cmd=REG&mac=22:33:44:55&gid=2211

"""
