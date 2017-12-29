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

### What do we expect to learn from this experiment?

What we are wondering here is whether or not, Kubernetes will indeed kill our
unhealthy pod, then start a new one within a given amount of time. This
experiment tells us whether we properly report our state to Kubernetes but
also if our liveness probe timings are sane.

But why does it matter? Well, if your service gets unhealthy and Kubernetes
cannot notice it (because of a missng liveness probe), or takes too long to
respond (because poorly tuned liveness probes), then our users may experience
poor responses from the service.

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

## Run the Experiment

You can now run the experiment as usual:

```console
$ chaos run experiment.json
[2017-12-29 18:14:46 INFO] Validating experiment's syntax
[2017-12-29 18:14:46 INFO] Experiment looks valid
[2017-12-29 18:14:46 INFO] Running experiment: Pod should be automatically killed and restarted when unhealthy
[2017-12-29 18:14:46 INFO] Steady state hypothesis: Services are all available and healthy
[2017-12-29 18:14:46 INFO] Probe: all-services-are-healthy
[2017-12-29 18:14:47 INFO] Probe: webapp-is-available
[2017-12-29 18:14:47 INFO] Steady state hypothesis is met, we can carry on!
[2017-12-29 18:14:47 INFO] Action: talk-to-webapp
[2017-12-29 18:14:47 INFO] Pausing before next activity for 15s...
[2017-12-29 18:15:02 INFO] Action: confirm-purchase
[2017-12-29 18:15:02 ERROR]   => failed: HTTP call failed with code 500 (expected 200): <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>500 Internal Server Error</title>
    <h1>Internal Server Error</h1>
    <p>The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.</p>
    
[2017-12-29 18:15:02 INFO] Pausing before next activity for 80s...
[2017-12-29 18:16:22 INFO] Probe: collect-how-many-times-our-service-container-restarted-in-the-last-minute
[2017-12-29 18:16:22 INFO] Probe: read-webapp-logs-for-the-pod-that-was-killed
[2017-12-29 18:16:22 INFO] Probe: read-webapp-logs-for-pod-that-was-started
[2017-12-29 18:16:22 INFO] Pausing before next activity for 10s...
[2017-12-29 18:16:32 INFO] Probe: collect-status-code-from-our-webapp-in-the-last-2-minutes
[2017-12-29 18:16:32 INFO] Pausing before next activity for 5s...
[2017-12-29 18:16:37 INFO] Probe: plot-request-latency-throughout-experiment
[2017-12-29 18:16:37 INFO] Let's rollback...
[2017-12-29 18:16:37 INFO] No declared rollbacks, let's move on.
[2017-12-29 18:16:37 INFO] Experiment ended with status: completed
```

This experiment first looks at the system steady state, it expects the webapp
to be available and healthy. Then, it starts talking to the application, on
its `/` endpoint in the background for one minute. After a little while, we
call the `/purchase/confirm` endpoint that fails. Following that event, we
expect the pod to be restarted once within the next 30 seconds. We also look
at the impact of the HTTP responses during that time.

## Generate a report

Once the experiment is finished, you may generate a report as per the
[documentation][reporting]:

[reporting]: http://chaostoolkit.org/usage/running/#generating-a-report

```
$ chaos report --export-format=pdf chaos-report.json chaos-report.pdf
```

This command is only available if you installed the
[chaostoolkit-reporting][chaosreport] library.

[chaosreport]: https://github.com/chaostoolkit/chaostoolkit-reporting

## Analysis

The [attached report][report], in this repository, is an example of such a run.

[report]: https://github.com/chaostoolkit/chaostoolkit-samples/blob/master/pod-should-be-restarted-when-service-is-unhealthy/chaos-report.pdf

The failure occured with the `confirm-purchase` call at 5:24:07pm. Looking at
page 7, we can start seeing `500 Server Error` errors showing up while `200 OK`
responses are stalled.

Looking at page 11, we see the logs from the application showing it received
`SIGTERM` at 5:24:19pm. This is already interesting because the Kubernetes
pod specification declared a [liveness probe][livenessprobe] with a check
period of 5s. It tells us Kubernetes decided after 3 attempts the application
was unhealthy and decided to [terminate][podterm] it.

[livenessprobe]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/
[podterm]: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods

Next, we see page 12, in the application logs, the new instance is ready to
accept requests around 5:24:28pm. Indeed, Prometheus shows us new `200 OK`
responses at 5:24:30pm.

We may wonder why the `500 Server Error` responses stalled quickly? Well, it
actually results from the polling frequency from Prometheus which was set to
every 5s against the application. The 500 increases from 4 to 9 at 5:24:15pm
but, as we saw, the application is terminated at 5:24:19pm, before the next
poll from Prometheus. In that case, since Prometheus is a time series database,
it keeps the last scraped value.

On page 5, we see that the count for pod restarting increased by 1 (as expected
in our experiment) at 5:24:42pm which is 15s after the pod was indeed restarted.
This 15s duration is the polling frequency of Kubernetes metrics by Prometheus.

We can therefore explain how an unhealthy pod is detected by Kubernetes and
restarted according to its policy. Next would be to improve the system so the
user doesn't experiment any downtime of service.

