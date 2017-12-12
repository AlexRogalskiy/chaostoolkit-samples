# -*- coding: utf-8 -*-
import uuid

from sanic import Sanic
from sanic.response import json, text
from sanic_prometheus import monitor

app = Sanic()


@app.route("/")
async def index(request):
    return json(str(uuid.uuid4()))


@app.route("/health")
async def health(request):
    return text("OK")


if __name__ == "__main__":
    monitor(app).expose_endpoint()
    app.run(host="0.0.0.0", port=8080)
