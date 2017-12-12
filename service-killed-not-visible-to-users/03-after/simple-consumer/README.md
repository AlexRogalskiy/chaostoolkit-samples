## Overview

A simple consumer service that calls a provider service via HTTP to fetch
a random value.

In this implementation, the consumer relies on a circuit-breaker to capture
the fact the provider may be gone (or faulty) and return a pre-defined message
back to the consumer's caller.

Notice that we set the health check to return `503 Unavailable` when the
circuit breaker is open, informing whoever is monitoring that this service is
no longer able to receive trafic.

## Build

Build the Docker image as follows:

```
$ docker build -t chaostoolkit/simple-consumer:after
```

