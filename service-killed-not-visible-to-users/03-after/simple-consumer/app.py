# -*- coding: utf-8 -*-
import os

import aiohttp
from failsafe import CircuitBreaker, Failsafe, FailsafeError, RetryPolicy
from sanic import Sanic
from sanic.response import json, text
from sanic_prometheus import monitor

app = Sanic()
circuit = CircuitBreaker(
    maximum_failures=3, 
    reset_timeout_seconds=10
)

failsafe = Failsafe(
    circuit_breaker=circuit,
    retry_policy=RetryPolicy()
)


@app.route("/")
async def index(request):
    return text("Hello world!")


@app.route("/health")
async def health(request):
    if circuit.current_state == "open":
        return text("Unavailable", status=503)

    return text("OK")


@app.route("/invoke")
async def invoke(request):
    async def _call_consumer(request):
        async with aiohttp.ClientSession() as client:
            provider_base_url = request.app.config["provider-url"]
            async with client.get(
                "{u}/".format(u=provider_base_url), timeout=5) as resp:
                return await resp.json()

    try:
        return json(await failsafe.run(lambda: _call_consumer(request)))
    except FailsafeError:
        return text("failed talking to the producer")


if __name__ == "__main__":
    monitor(app).expose_endpoint()
    provider_url = "http://{h}:{p}"
    app.config["provider-url"] = provider_url.format(
        h=os.environ.get("MY_PROVIDER_APP_HOST", "my-provider-service"),
        p=os.environ.get("MY_PROVIDER_APP_PORT", "8080")
    )
    app.run(host="0.0.0.0", port=8080)
