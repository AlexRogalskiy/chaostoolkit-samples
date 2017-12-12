# -*- coding: utf-8 -*-
import os

import aiohttp
from sanic import Sanic
from sanic.response import json, text
from sanic_prometheus import monitor

app = Sanic()


@app.route("/")
async def index(request):
    return text("Hello world!")


@app.route("/health")
async def health(request):
    return text("OK")


@app.route("/invoke")
async def invoke(request):
    async with aiohttp.ClientSession() as client:
        provider_base_url = request.app.config["provider-url"]
        async with client.get(
            "{u}/".format(u=provider_base_url), timeout=5) as resp:
            return json(await resp.json())


if __name__ == "__main__":
    monitor(app).expose_endpoint()
    provider_url = "http://{h}:{p}"
    app.config["provider-url"] = provider_url.format(
        h=os.environ.get("MY_PROVIDER_APP_HOST", "my-provider-service"),
        p=os.environ.get("MY_PROVIDER_APP_PORT", "8080")
    )
    print("Provider is at {p}".format(p=app.config["provider-url"]))
    app.run(host="0.0.0.0", port=8080)
