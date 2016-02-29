from flask import Flask, request, jsonify, make_response

class WatchFlask(Flask):
    def __init__(self):
        Flask.__init__(self, __name__)

    @classmethod
    def setWatcher(cls, watcher):
        cls.watcher = watcher

server = WatchFlask()

def get_threads_stats():
    return [{ 'id': x.thread_id, 'state': x.state } for x in server.watcher.scheduler.pool]

def get_tasks():
    return [x.to_dict() for x in server.watcher.tasks]

@server.route("/api/stats/threads")
def threads():
    threads = get_threads_stats()
    return jsonify({ 'threads': threads })

@server.route("/api/stats/tasks")
def tasks():
    tasks = get_tasks()
    return jsonify({ 'tasks': tasks })

@server.route("/api/data/<table>")
def data(table):
    try:
        data = server.watcher.tables[table].table
    except KeyError:
        return make_response(jsonify({ 'error': 'table %s not found' % table }), 404)
    return jsonify({ 'data': data })

@server.route("/api/data/<table>/<varname>")
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