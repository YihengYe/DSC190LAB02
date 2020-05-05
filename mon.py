import time
import datetime

def process_db():
	now = datetime.datetime.now()
	print(now.strftime("%Y-%m-%d %H:%M:%S")," I'm checking for timeout")



#========== MAIN ===========
while True:
	process_db()
	time.sleep(5)

