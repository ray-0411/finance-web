from datetime import datetime
from zoneinfo import ZoneInfo

TAIPEI = ZoneInfo("Asia/Taipei")

def t_now():
    return datetime.now(TAIPEI)

def t_today():
    return datetime.now(TAIPEI).date()