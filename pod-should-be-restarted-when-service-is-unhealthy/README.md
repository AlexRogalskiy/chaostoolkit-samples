# "Pod should be automatically killed and restarted when unhealthy" Sample Chaos Experiment

This sample experiment shows the impact of degraded service capabilities on
our global system state. Unlike other samples, this one does not
showcase a `before` and `after` steps but shows how the Chaos Toolkit is also
great to simply ask open questions and gather data, through probes, that allow
you to analyse your system.

## The Experimental Context

You run a webapp (over HTTP), with a single instance, which is monitored by
Kubernetes through its `/health` endpoint. At some point, the
`/purchase/endpoint` is called and triggers a service failure. We want to use
that knowledge to see if Kubernetes does pick it up and restart the pod as per
the deploymet's liveness probe.

## Prerequisites

To run this you will need the [Chaos Toolkit CLI][chaos-toolkit] >= 0.6.0
installed and have access to a Kubernetes cluster. For simplicity in getting
up and running we assume you're using a local [minikube][] here. 

[minikube]: https://kubernetes.io/docs/getting-started-guides/minikube/
[chaos-toolkit]: https://github.com/chaostoolkit/chaostoolkit

### Chaos Toolkit Dependencies

Make sure to install the latest chaostoolkit CLI:

```shell
(venv) $ pip install -U chaostoolkit
```

You will also need to install the [chaostoolkit-kubernetes][chaosk8s]
extension:

```shell
(venv) $ pip install -U chaostoolkit-kubernetes
```

[chaosk8s]: https://github.com/chaostoolkit/chaostoolkit-kubernetes

### Vegata Tool

This experiment runs the [vegeta][] cli to talk our application. It is a
simple binary that needs to be in your `PATH`.

[vegeta]: https://github.com/tsenart/vegeta

### Kubernetes

If you running minikube, you may want to create your stack as follows:

```
$ minikube delete
$ minikube start --cpus=2 --memory=2048
```

If not, make sure either you have the Kubernetes config under `~/kube` or
amend the experiment file to add secrets with the appropriate credentials.
See the [chaostoolkit-kubernetes][chaosk8s] extension.

### Helm

We use [Helm][helm] to deploy further dependencies such as Prometheus. Install
its [command line][helmcli] and then run:

```console
$ helm init
```

Give it a minute before it settles.

[helm]: https://github.com/kubernetes/helm
[helmcli]: https://github.com/kubernetes/helm#install

#### Prometheus

This experiment collects datapoints from a Prometheus running in the Kubernetes
cluster. 

You can install it as follows:

```console
$ helm install --name prometheus --set server.service.type=NodePort --values=values.yaml stable/prometheus
```

## Setup the Experiment

Before you can run the experiment itself, you must deploy the application:

```console
$ kubectl create -f webapp-deployment.json -f webapp-service.json
```

Once the deployment has settled, you must run the following:

```console
$ export WEBAPP_SERVICE_ADDR=$(minikube service webapp-service --url)
$ export PROMETHEUS_ADDR=$(minikube service prometheus-prometheus-server --url)
$ echo "GET ${WEBAPP_SERVICE_ADDR}/" > urls.txt
```

These commands need only be run when you create the Kubernetes service
resource or when you deploy Prometheus. Not everytime you run the experiment.

## Run the Experiment

You can now run the experiment as usual:

```console
$ chaos run experiment.json
[2017-12-28 21:43:00 INFO] Validating experiment's syntax
[2017-12-28 21:43:01 INFO] Experiment looks valid
[2017-12-28 21:43:01 INFO] Running experiment: Pod should be automatically killed and restarted when unhealthy
[2017-12-28 21:43:01 INFO] Steady state hypothesis: Services are all available and healthy
[2017-12-28 21:43:01 INFO] Probe: all-services-are-healthy
[2017-12-28 21:43:01 INFO] Probe: webapp-is-available
[2017-12-28 21:43:01 INFO] Steady state hypothesis is met, we can carry on!
[2017-12-28 21:43:01 INFO] Action: talk-to-webapp
[2017-12-28 21:43:01 INFO] Pausing before next activity for 15s...
[2017-12-28 21:43:16 INFO] Action: confirm-purchase
[2017-12-28 21:43:16 ERROR]   => failed: HTTP call failed with code 500 (expected 200): <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>500 Internal Server Error</title>
    <h1>Internal Server Error</h1>
    <p>The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.</p>
    
[2017-12-28 21:43:16 INFO] Pausing before next activity for 30s...
[2017-12-28 21:43:46 INFO] Probe: collect-how-many-times-our-service-container-restarted-in-the-last-minute
[2017-12-28 21:43:46 INFO] Pausing before next activity for 10s...
[2017-12-28 21:43:56 INFO] Probe: collect-status-code-from-our-webapp-in-the-last-2-minutes
[2017-12-28 21:43:56 INFO] Pausing before next activity for 5s...
[2017-12-28 21:44:01 INFO] Probe: plot-request-latency-throughout-experiment
[2017-12-28 21:44:10 INFO] Let's rollback...
[2017-12-28 21:44:10 INFO] No declared rollbacks, let's move on.
[2017-12-28 21:44:10 INFO] Experiment ended with status: completed
```

This experiment first looks at the system steady state, it expects the webapp
to be available and healthy. Then, it starts talking to the application, on
its `/` endpoint in the background for one minute. After a little while, we
call the `/purchase/confirm` endpoint that fails. Following that event, we
expect the pod to be restarted once within the next 30 seconds. We also look
at the impact of the HTTP responses during that time.

## Generate a report

Once the experiment is finished, you may generate a report as per the
[documentation][reporting].

[reporting]: http://chaostoolkit.org/usage/running/#generating-a-report

