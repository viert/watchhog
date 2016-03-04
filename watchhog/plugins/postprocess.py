from datetime import datetime
from dateutil import parser as dateparser
import logging
import unittest


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


def join(record, new_field, delimiter, *args):
    try:
        record[new_field] = delimiter.join([record[x] for x in args])
    except Exception as e:
        logging.error("Error in postprocess.join(): " + str(e))


def split(record, field, delimiter, new_field=None):
    if new_field is None:
        new_field = field
    try:
        array = record[field].split(delimiter)
    except Exception as e:
        logging.error("Error in postprocess.split(): " +  str(e))
        return
    record[new_field] = array
    for i, value in enumerate(array):
        record["%s_%d" % (new_field, i)] = value

exports = [to_datetime, to_float, to_int, join, split]