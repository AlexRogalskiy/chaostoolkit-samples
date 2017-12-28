# -*- coding: utf-8 -*-
import random
import time

import cherrypy
from cherrypy.process.wspbus import states
from flask import abort, Flask, request
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
metrics = PrometheusMetrics(app)
state = {
    "running": True,
    "last_check": time.time()
}


@app.route('/')
@metrics.summary('http_index_requests_by_status',
                 'Request latencies by status',
                 labels={'status': lambda r: r.status_code})
@metrics.histogram('http_index_requests_by_status_and_path', 
                   'Index requests latencies by status and path',
                   labels={
                       'status': lambda r: r.status_code,
                       'path': lambda: request.path})
def index():
    if not state["running"]:
        return abort(500)
    return 'Hello World!'


@app.route("/purchase/confirm")
@metrics.summary('http_purchase_confirm_requests_by_status',
                 'Request latencies by status',
                 labels={'status': lambda r: r.status_code})
@metrics.histogram('http_purchase_confirm_requests_by_status_and_path', 
                   'Purchase confirm request latencies by status and path',
                   labels={
                       'status': lambda r: r.status_code,
                       'path': lambda: request.path})
def confirm():
    state["running"] = False
    state["last_check"] = time.time()
    return abort(500)


@app.route('/health')
@metrics.summary('http_health_requests_by_status',
                 'Request latencies by status',
                 labels={'status': lambda r: r.status_code})
@metrics.histogram('http_health_requests_by_status_and_path', 
                   'Health request latencies by status and path',
                   labels={
                       'status': lambda r: r.status_code,
                       'path': lambda: request.path})
def health():
    now = time.time()
    if now - state["last_check"] >= 40:
        state["running"] = True
        state["last_check"] = time.time()

    if not state["running"]:
        return abort(503)

    return "OK"


if __name__ == '__main__':
    cherrypy.config.update({
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8080,
        "engine.autoreload.on": False
    })

    cherrypy.tree.graft(app.wsgi_app)
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
