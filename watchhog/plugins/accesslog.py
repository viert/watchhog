import logging


def rps_by_vhost(store, vhost_field='vhost', date_field_name='datetime'):
    dtkeys = store.get_field_keys(date_field_name)
    if dtkeys is None:
        logging.error('rps_by_host() needs "%s" field indexed to work properly' % date_field_name)
        return {}
    vhost_counters = store.get_field_counter(vhost_field)
    if vhost_counters is None:
        logging.error('rps_by_host() needs "%s" field indexed to work properly' % vhost_field)
        return {}

    timedelta = dtkeys[-1] - dtkeys[0]
    rps = {}

    for host,value in vhost_counters.items():
        rps[host] = float(value) / timedelta

    rps['__total__'] = sum(rps.values())
    return rps


exports = [rps_by_vhost]