from datetime import datetime, timedelta
from pytz import timezone
import time
import ast

date_str = "Fri Sep 06 23:48:53 +0000 2019"
date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date_str, '%a %b %d %H:%M:%S +0000 %Y'))
datetime_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))
datetime_obj_utc.replace(second=0, microsecond=0, minute=0, hour=datetime_obj_utc.hour)+" "+ timedelta(hours=datetime_obj_utc.minute//30)
print(datetime_obj_utc)

list={"A":1,"B":2}
list=str(list)
dicty=ast.literal_eval(list)