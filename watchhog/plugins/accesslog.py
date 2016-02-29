import logging

def rps_by(store, field=None, datetime_field_name='datetime'):
    if field is None:
        logging.error("count_by_field(field) field can't be None")

    dtkeys = store.get_field_keys(datetime_field_name)

    if dtkeys is None:
        logging.error('count_by_field() needs "%s" field indexed to work properly' % datetime_field_name)
        return {}

    counters = store.get_field_counter(field)
    if counters is None:
        logging.error('count_by_field() needs "%s" field indexed to work properly' % field)
        return {}

    timedelta = dtkeys[-1] - dtkeys[0]
    rps = {}

    for fieldvalue, count in counters.items():
        rps[fieldvalue] = float(count) / timedelta.total_seconds()

    rps['__total__'] = sum(rps.values())
    return rps


exports = [rps_by]