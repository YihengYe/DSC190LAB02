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
    
    try:
        if is_get:
            mac = params['mac'].value
        else:
            mac = params['mac']
    except:
        mac = None
        
    
    if (not gid) and (not mac):
        sql = "SELECT * FROM iotdb.devices"
    elif (not mac):
        sql = "SELECT * FROM iotdb.devices WHERE groupID=%s" % gid
    else:
        sql="SELECT * FROM iotdb.devices WHERE mac='{0}'".format(mac)

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
    
    try:
        if is_get:
            mac = params['mac'].value
        else:
            mac = params['mac']
    except:
        mac = None
    
    if (not gid) and (not mac):
        sql = "SELECT * FROM iotdb.devlogs LIMIT 5"
    elif (not mac):
        sql = "SELECT * FROM iotdb.devlogs WHERE groupID='{0}' ORDER BY devlogID DESC limit 5".format(gid)
    elif (not gid):
        sql = "SELECT * FROM idtdb.devlogs WHERE mac='{0}' ORDER BY devlogID DESC limit 5".format(mac)
    else:
        sql ="SELECT * FROM idtdb.devlogs WHERE mac='{0}' and groupID='{1}' ORDER BY devlogID DESC limit 5".format(mac, gid)
        

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
    
    try:
        if is_get:
            mac = params['devmac'].value
        else:
            mac = params['devmac']
    except:
        mac = None
    
    if (not gid) and (not mac): # blelog_id
        sql = "SELECT * FROM iotdb.blelogs ORDER BY blelog_id  DESC LIMIT 5"
    elif (not mac):
        sql = "SELECT * FROM iotdb.blelogs WHERE gid='{0}' ORDER BY blelog_id DESC LIMIT 5".format(gid)
    elif (not gid):
        sql = "SELECT * FROM iotdb.blelogs WHERE devmac='{0}' ORDER BY blelog_id DESC LIMIT 5".format(mac)
    else:
        sql = "SELECT * FROM iotdb.blelogs WHERE devmac='{0}' AND gid='{1}' ORDER BY blelog_id DESC LIMIT 5".format(mac, gid)


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
        print(dev_update  + 'err here')

    try:
        beacons = params['beacons']
        sql="INSERT INTO iotdb.blelogs(gid, devmac, blemac, blerssi, timestamp) VALUES "
        bec_dict=[]
        for idx, i in enumerate(beacons):
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
            if blemac in bec_dict:
                if idx==len(beacons)-1:
                    row ="('{0}', '{1}', '{2}', '{3}','{4}')".format(gid, devmac, blemac, blerssi, rntime)
                    sql=sql+row+';'

            else:
                row ="('{0}', '{1}', '{2}', '{3}','{4}')".format(gid, devmac, blemac, blerssi, rntime)
                bec_dict.append(blemac)
                if idx<len(beacons)-1:
                    sql=sql+row+','
                else:
                    sql=sql+row+';'

        try:
            execute_sql(sql, cursor)
            connection.commit()

            status='successed'
        except Exception as err:
            print(err)
            status="failed"
        format_result(['timestamp', 'status'], [time, status])
    except Exception as err:
        print(err)
        print(dev_update)


    

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



def forecast(cursor):
    url="http://api.openweathermap.org/data/2.5/weather?zip=92037,us&appid=0354c29c5e773c46d37727c8a0455d58"
    r=requests.get(url)
    data=r.json()
    gid='03'
    privoder="open weather"
    maininfo=data['main']
    temp=maininfo['temp']
    min_temp=maininfo['temp_min']
    max_temp=maininfo['temp_max']
    hum=maininfo['humidity']
    sql="INSERT INTO iotdb.forecast(gid, temp, min_temp, max_temp, hum, timestamp, provider)\
         VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(gid, temp, min_temp, max_temp, hum, time, privoder)

    try:
        execute_sql(sql, cursor)
        connection.commit()

        status='successed'
    except Exception as err:
        print(err)
        status="failed"
    format_result(['timestamp', 'status'], [time, status])
    
def logmc(cursor, params):
    temp=params['temp']
    gid=params['gid']
    hum=params['hum']
    mac=params['mac']
    devstatus='ACTIVE'
    
    sql="INSERT INTO iotdb.mcdata(gid, temp, hum, timerstamp, status, mac)\
         VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')".format(gid,temp,hum,time, devstatus, mac)
    try:
        execute_sql(sql, cursor)
        connection.commit()

        status='successed'
    except Exception as err:
        print(err)
        status="failed"
    format_result(['timestamp', 'status'], [time, status])

    dev_update="UPDATE iotdb.devices SET lastseen='{0}' WHERE groupID='{1}' AND mac='{2}'".format(time, gid, mac)
    try:
        execute_sql(dev_update, cursor)
        connection.commit()

        status='successed'
    except Exception as err:
        print(err)
        status="failed"
    format_result(['timestamp', 'status'], [time, status])


def post_weather(cursor,params):
    mac=params['devmac']
    sql="SELECT avg(temp) as avg_temp, avg(hum) as avg_hum, HOUR(timerstamp) as hour, DATE(timerstamp) as date FROM iotdb.mcdata \
        WHERE mac='{0}' AND NOW()<=DATE_ADD(timerstamp, INTERVAL 120 HOUR) GROUP BY hour".format(mac)
    try:
        data = execute_sql(sql, cursor)
    except Exception as err:
        print(err)
    display_data(data, 'weather')



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
    if cmd_line =='FORECAST':
        forecast(cursor)
    
    if cmd_line=='LOGMC':
        logmc(cursor, params)
    
    if cmd_line=="WEATHER":
        post_weather(cursor, params)



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
