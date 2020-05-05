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


def process_db():
	now = datetime.now()
	print(now.strftime("%Y-%m-%d %H:%M:%S")," I'm checking for timeout")
	



#========== MAIN ===========
while True:
	process_db()
	time.sleep(5)

