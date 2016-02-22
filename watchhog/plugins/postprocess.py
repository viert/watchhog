from datetime import datetime
from dateutil import parser as dateparser


def to_datetime(record, key, frmt=None):
    if frmt is None:
        dt = dateparser.parse(record[key])
    else:
        dt = datetime.strptime(record[key], frmt)
    record[key] = dt


def to_float(record, key, default=None):
    try:
        record[key] = float(record[key])
    except ValueError:
        if not default is None:
            record[key] = default


def to_int(record, key, base=10, default=None):
    try:
        record[key] = int(record[key], base)
    except ValueError:
        if not default is None:
            record[key] = default

exports = [to_datetime, to_float, to_int]