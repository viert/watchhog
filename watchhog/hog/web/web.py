import os
from flask import Flask, jsonify, make_response, send_file, request


class WatchFlask(Flask):
    def __init__(self, *args, **kwargs):
        Flask.__init__(self, *args, **kwargs)

    @classmethod
    def setWatcher(cls, watcher):
        cls.watcher = watcher


static_folder = os.path.join(os.path.dirname(__file__), 'static')
server = WatchFlask(__name__, static_url_path='', static_folder=static_folder)


def get_host_header():
    return request.headers['Host']


def get_threads_stats():
    return [{ 'id': x.thread_id, 'state': x.state } for x in server.watcher.scheduler.pool]


def get_tasks():
    return [x.to_dict() for x in server.watcher.tasks]


@server.route("/")
def index():
    return send_file(os.path.join(static_folder, 'index.html'))


@server.route("/api/stats/threads")
def threads():
    threads = get_threads_stats()
    return jsonify({ 'threads': threads })


@server.route("/api/stats/tasks")
def tasks():
    tasks = get_tasks()
    return jsonify({ 'tasks': tasks })


@server.route("/api/tables")
def table_list():
    table_names = server.watcher.tables.keys()
    data = [{ 'name': x, 'link': "http://%s/api/tables/%s" % (get_host_header(), x)} for x in table_names]
    return jsonify({ 'tables': data })


@server.route("/api/tables/<table>")
def table_overview(table):
    try:
        store = server.watcher.tables[table]
    except KeyError:
        return make_response(jsonify({ 'error': 'table %s not found' % table }), 404)

    variables = store.vars.keys()
    variables = [{ 'name': x, 'link': "http://%s/api/tables/%s/variables/%s" % (get_host_header(), table, x)} for x in variables]

    indexes = []
    for key, index in store.indexes.items():
        data = {
            'name': key,
            'type': 'simple' if 'keys' in index else 'compound',
            'keys_count': len(index['keys']) if 'keys' in index else len(index['index'])
        }
        indexes.append(data)

    data = {
        'name': table,
        'indexes': indexes,
        'variables': variables,
        'record_count': len(store.table),
        'data_link': "http://%s/api/tables/%s/data" % (get_host_header(), table)
    }
    if data['record_count'] > 0:
        record = store.table[0]
        data['field_names'] = record.keys()
    else:
        data['field_names'] = []
    return jsonify({ 'table': data })



@server.route("/api/tables/<table>/data")
def data(table):
    try:
        data = server.watcher.tables[table].table
    except KeyError:
        return make_response(jsonify({ 'error': 'table %s not found' % table }), 404)
    return jsonify({ 'data': data })


@server.route("/api/tables/<table>/variables/<varname>")
def variable(table, varname):
    try:
        store = server.watcher.tables[table]
    except KeyError:
        return make_response(jsonify({ 'error': 'table %s not found' % table }), 404)
    try:
        value = store.vars[varname]
    except KeyError:
        return make_response(jsonify({ 'error': 'variable %s not found in table %s' % (varname, table) }), 404)
    return jsonify({ 'data': value })