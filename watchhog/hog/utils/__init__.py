from datetime import datetime

def format_date(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
    except:
        return "undef"