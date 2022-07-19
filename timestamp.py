from datetime import datetime

def now():
  now = datetime.now()
  timestamp = now.strftime("%Y-%m-%dT%H.%M.%S")
  return timestamp
  #print(timestamp)
 

