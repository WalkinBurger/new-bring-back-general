import time
import datetime

t = "02-Jan-23 10:37 AM"
print(time.mktime(datetime.datetime.strptime(t, "%d-%b-%y %I:%M %p").timetuple()))