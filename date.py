import datetime

def today_date():
    now  = datetime.datetime.now()
    day  = now.strftime('%Y-%m-%d')
    hour = now.strftime('%H:%M:%S')
    return {'day':day, 'hour':hour}