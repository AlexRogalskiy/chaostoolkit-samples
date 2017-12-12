## Overview

A simple consumer service that calls a provider service via HTTP to fetch
a random value.

In this implementation, the consumer does not check, nor handle, that the
provider is actually there so breaks miserably when it is not.

## Build

Build the Docker image as follows:

```
$ docker build -t chaostoolkit/simple-consumer:before
```

