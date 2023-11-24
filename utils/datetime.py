import datetime


def timestampToDate(timestamp):
  date_time = datetime.datetime.fromtimestamp(timestamp)
  return date_time.strftime("%Y-%m-%d")

def timestampToDateWithTime(timestamp):
  date_time = datetime.datetime.fromtimestamp(timestamp)
  return date_time.strftime("%Y-%m-%d %H:%M")