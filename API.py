#!/usr/bin/python
import os
import pymysql
import sys
import json
import requests
from flask import Flask, request
from datetime import date
from datetime import datetime
import time as tts
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
    print(data.replace('None', "\"null\""))
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


def get_list(params, cursor, is_get):
    try:
        if is_get:
            gid = params['gid'].value
        else:
            gid = params['gid']
    except:
        gid = None
    
    if (not gid):
        sql = "SELECT * FROM iotdb.devices"
    else:
        sql = "SELECT * FROM iotdb.devices WHERE groupID=%s" % gid

    data = execute_sql(sql, cursor)
    for item in data:
       item['lastseen'] = str(item['lastseen'])
    
    display_data(data, 'devices')

def get_devlist(params, cursor, is_get):
    try:
        if is_get:
            gid = params['gid'].value
        else:
            gid = params['gid']
    except:
        gid = None
    
    if (not gid):
        sql = "SELECT * FROM iotdb.devlogs"
    else:
        sql = "SELECT * FROM iotdb.devlogs WHERE groupID=%s" % gid

    data = execute_sql(sql, cursor)
    for item in data:
       item['lastseen'] = str(item['lastseen'])
    
    display_data(data, 'devlogs')

def get_blelist(params, cursor, is_get):
    try:
        if is_get:
            gid = params['gid'].value
        else:
            gid = params['gid']
    except:
        gid = None
    
    if (not gid): # blelog_id
        sql = "SELECT * FROM iotdb.blelogs ORDER BY blelog_id  DESC LIMIT 10"
    else:
        sql = "SELECT * FROM iotdb.blelogs WHERE gid='{0}' ORDER BY blelog_id DESC LIMIT 10".format(gid)

    data = execute_sql(sql, cursor)
    for item in data:
       item['timestamp'] = str(item['timestamp'])
    
    display_data(data, 'blelogs')


def get_groups(params, cursor, is_get):
    if 'gid' not in params.keys():
        sql = "SELECT groupName,Student_1,Student_2 FROM iotdb.groups"
    else:
        if is_get:
            gid = params['gid'].value
        else:
            gid = params['gid']
        sql= "SELECT groupName,Student_1,Student_2 FROM iotdb.groups WHERE groupID=%s" % gid
    data = execute_sql(sql, cursor)
    display_data(data, 'groups')
    

def get_reg(params, cursor, is_get):
    if is_get:
        mac = params['mac'].value
        gid = params['gid'].value
    else:
        mac = params['mac']
        gid = params['gid']

    query = "SELECT * FROM iotdb.devices WHERE iotdb.devices.mac = '%s'" % mac
    data = execute_sql(query, cursor)

    # if the device is not registered, insert the new
    if len(data) < 1:
        divi_sql = "INSERT INTO iotdb.devices(mac, groupID, lastseen) \
                    VALUES('{0}', '{1}', '{2}')".format(mac, 
                    gid, 
                    time)
    # if an existing device, update the origin
    else:
        divi_sql="UPDATE iotdb.devices \
            SET lastseen='{0}', groupID='{1}' \
            WHERE mac='{2}'".format(time,
             gid, 
             mac) 
    try:
        execute_sql(divi_sql, cursor)
        connection.commit()
        status='successed'
        
    except Exception as err:
        status = 'failed'
        print(err)

    format_result(['mac', 'time', 'status'], [mac, time, status])


def get_log(params, cursor, is_get):
    if is_get:
        gid = params['gid'].value
        devmac = params['devmac'].value
        ip=params['ip'].value
        lat=params['dev_lat'].value
        lon=params['dev_long'].value
    else:
        gid = params['gid']
        devmac = params['devmac']
        ip=params['ip']
        lat=params['dev_lat']
        lon=params['dev_long']
    
    check = "SELECT * FROM iotdb.devices WHERE iotdb.devices.mac = '{0}' \
             AND iotdb.devices.groupID = '{1}'".format(devmac, gid)
    data = execute_sql(check, cursor)
    # if the device is not registered, insert the new
    if len(data) < 1:
        dev_update = "INSERT INTO iotdb.devices(mac, groupID, lastseen, ip, dev_lat, dev_long) \
                    VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(devmac, 
                    gid, 
                    time,
                    ip,
                    lat,
                    lon)
    # if an existing device, update the origin
    else:
        dev_update="UPDATE iotdb.devices\
        SET lastseen='{0}',ip='{1}', dev_lat='{2}', dev_long='{3}'\
        WHERE mac='{4}' AND groupID='{5}'".format(time, ip, lat, lon, devmac, gid)
        # check null value
        checker=data[0]
        checker_ip=checker['ip']
        checker_lat=checker['dev_lat']
        if checker_ip==None:
            dev_update="UPDATE iotdb.devices\
            SET lastseen='{0}',ip='{1}', dev_lat='{2}', dev_long='{3}'\
            WHERE mac='{4}' AND groupID='{5}' AND ip is null".format(time, ip, lat, lon, devmac, gid)
        if checker_lat==None:
            dev_update="UPDATE iotdb.devices\
            SET lastseen='{0}',ip='{1}', dev_lat='{2}', dev_long='{3}'\
            WHERE mac='{4}' AND groupID='{5}' AND dev_lat is null AND dev_long is null".format(time, ip, lat, lon, devmac, gid)
    try:
        cursor.execute(dev_update)
        connection.commit()

    except Exception as err:
        print(err)
        print(dev_update)

    beacons = params['beacons']
    # log into blelogs
    for i in beacons:
        if is_get:
            gid = params['gid'].value
            blemac = i['mac'].value
            devmac = params['devmac'].value
            blerssi = i['rssi'].value
        else:
            gid = params['gid']
            blemac = i['mac']
            devmac = params['devmac']
            blerssi = i['rssi']
        rntime=get_global_time()

        sql = "INSERT INTO iotdb.blelogs(gid, devmac, blemac, blerssi, timestamp) \
            VALUES('{0}', '{1}', '{2}', '{3}','{4}')".format(gid, devmac, blemac, blerssi, rntime)

        try:
            execute_sql(sql, cursor)
            connection.commit()

            status='successed'
        except Exception as err:
            print(err)
            status="failed"

        format_result(['timestamp', 'status'], [time, status])
        tts.sleep(0.5)


# def post_reg(params, cursor):
#     mac = params['mac']
#     query = "SELECT * FROM iotdb.devices WHERE iotdb.devices.mac = '%s'" % mac
#     data = execute_sql(query, cursor)

#     # if the device is not registered, insert the new
#     if len(data) < 1:
#         divi_sql = "INSERT INTO iotdb.devices(mac, groupID, ip, lastseen) \
#                     VALUES('{0}', '{1}', '{2}', '{3}')".format(mac, 
#                     params['gid'], 
#                     params['ip'],
#                     time)
#     # if an existing device, update the origin
#     else:
#         divi_sql="UPDATE iotdb.devices \
#             SET ip='{0}', groupID='{1}', lastseen='{2}' \
#             WHERE mac='{3}'".format(params['ip'],
#              params['gid'], 
#              time,
#              mac) 
#     try:
#         execute_sql(divi_sql, cursor)
#         connection.commit()
#         status='successed'
        
#     except Exception as err:
#         status = 'failed'
#         print(err)

#     format_result(['mac', 'time', 'status'], [mac, time, status])

def post_logdev(params, cursor, is_get):
    assert is_get == False, 'LOGDEV not supported for GET'

    mac = params['mac']
   
    divi_sql = "INSERT INTO iotdb.devlogs(mac, groupID, RSSI, lastseen) \
                VALUES('{0}', '{1}', '{2}', '{3}')".format(mac, 
                params['gid'], 
                params['RSSI'],
                time)
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
    # print("DSC190 API version 0.0.3")

    #GET URL, see my example urls at bottom, we write four functions together
    if os.environ['REQUEST_METHOD']=='GET':
        GET=True
    elif os.environ['REQUEST_METHOD']=='POST':
        GET=False
    else:
        print('only GET and POST are supportted')
        sys.exit(0)
    if GET:
        params = cgi.FieldStorage()
        cmd_line = params['cmd'].value.upper()
    else:
        params=json.load(sys.stdin)
        cmd_line = params['cmd'].upper()
        # print(json.dumps(params))
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

    if cmd_line == 'LIST':
        get_list(params, cursor, GET)

    if cmd_line == 'GROUPS':
        get_groups(params, cursor, GET)

    if cmd_line == 'REG':
        get_reg(params, cursor, GET)

    if cmd_line == 'LOG':
        get_log(params, cursor, GET)

    if cmd_line == 'LOGDEV':
        post_logdev(params, cursor, GET)
    if cmd_line =='BLELIST':
        get_blelist(params, cursor, GET)
    if cmd_line =='DEVLIST':
        get_devlist(params, cursor, GET)


  #   if GET:
  #       if params['cmd'].value.upper() == 'LIST':
  #           get_list(params, cursor)

  #       if params['cmd'].value.upper() == 'GROUPS':
  #           get_groups(params, cursor)

  #       if params['cmd'].value.upper() == 'REG':
  #           get_reg(params, cursor)

  #       if params['cmd'].value.upper() == 'LOG':
  #           get_log(params, cursor)
  #   else:
  #   	if params['cmd'] == 'LIST':
  #   		post_list(params, cursor)

		# if params['cmd'] == 'GROUPS':
  #   		post_groups(params, cursor)

  #       if params['cmd'] == 'REG':
  #           post_reg(params, cursor)

  #       if params['cmd'] == 'LOGDEV':
  #           post_logdev(params, cursor)

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
