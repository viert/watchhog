import logging

def rps_by(store, field=None, datetime_field_name='datetime'):
    if field is None:
        logging.error("rps_by(field) field can't be None")

    dtkeys = store.get_field_keys(datetime_field_name)

    if dtkeys is None:
        logging.error('rps_by() needs "%s" field indexed to work properly' % datetime_field_name)
        return {}

    counters = store.get_field_counter(field)
    if counters is None:
        logging.error('rps_by() needs "%s" field indexed to work properly' % field)
        return {}

    timedelta = dtkeys[-1] - dtkeys[0]
    rps = {}

    for fieldvalue, count in counters.items():
        rps[fieldvalue] = float(count) / timedelta.total_seconds()

    rps['__total__'] = sum(rps.values())
    return rps

def timings_by(store, field=None, request_time_field_name=None):
    if field is None or request_time_field_name is None:
        logging.error("You must explicitly provide field and request_time_field names for timings_by(field, request_time_field)")

    index_key = "%s.%s" % (field, request_time_field_name)
    counters = store.get_field_counter(index_key)

    if counters is None:
        logging.error("timings_by(%s, %s) needs index by %s" % (field, request_time_field_name, index_key))

    return counters

def timings(store, request_time_field_name=None):
    if request_time_field_name is None:
        logging.error("You must explicitly provide field and request_time_field names for timings(request_time_field)")

    counters = store.get_field_counter(request_time_field_name)
    if counters is None:
        logging.error("timings(%s) needs the field %s indexed" % (request_time_field_name, request_time_field_name))
    return counters

def status_codes_by_vhost(store, vhost_field='vhost', status_field='status'):
    index_key = '%s.%s' % (vhost_field, status_field)
    counters = store.get_field_counter(index_key)
    if counters is None:
        logging.error("status_codes_by_vhost needs index by %s" % index_key)
    return counters

exports = [rps_by, timings_by, timings, status_codes_by_vhost]