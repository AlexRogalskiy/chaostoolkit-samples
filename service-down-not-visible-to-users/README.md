
# "Service Down Not Visible To Users" Sample Chaos Experiment

This sample experiment demonstrates a simple learning loop where the `before`
conditions are such that the  services don't use circuit breakers and so
undesirable weaknesses will be exposed, and the `after` conditions are such
that same experiment will now not raise the same concerns once something like a
circuit breaker has been introduced.

More will be coming soon how Chaos Experiments help you achieve double-loop
learning in the main Chaos Toolkit documentation.

## Prerequisites

To run this you will need the [Chaos Toolkit CLI][chaos-toolkit] >= 0.3.0
installed and have access to a Kubernetes cluster. For simplicity in getting
up and running we assume you're using a local [minikube][] here.

```shell
(venv) $ pip install -U chaostoolkit
```

[chaos-toolkit]: https://github.com/chaostoolkit/chaostoolkit
[minikube]: https://kubernetes.io/docs/getting-started-guides/minikube/

You will also need to install the [chaostoolkit-kubernetes][chaosk8s] extension:

```shell
(venv) $ pip install -U chaostoolkit-kubernetes
```

[chaosk8s]: https://github.com/chaostoolkit/chaostoolkit-kubernetes

## Running the Experiment to Discover the `before` Weaknesses

Once you have the prerequisites in place you can deploy the `before` conditions
of the application as follows:

```shell
$ kubectl create -f consumer-service.json
$ kubectl create -f provider-service.json
$ kubectl create -f 01-before/provider-deployment.json
$ kubectl create -f 01-before/consumer-deployment.json
``` 

Once the deployments have settled you need to make a note of the URL at which
you can now reach the consumer service. If you are running minikube you can find
this URL using the following command:

```shell
$ minikube service my-consumer-service --url
```

With the URL in hand you can now edit the `experiment.json` file towards the end
to set the URL for the last probe in the experiment.

To run the experiment against the `before` conditions use the Chaos Toolkit CLI:

```shell
(venv) $ chaos run experiment.json
```

The experiment will highlight a weakness in that the consumer endpoint failed
to reply when this is what we would expect even when the producer has failed as
shown in the following experiment sample output:

```shell
[2017-12-06 16:38:01 INFO] Validating experiment's syntax
[2017-12-06 16:38:01 INFO] Experiment looks valid
[2017-12-06 16:38:01 INFO] Running experiment: System is resilient to provider's failures
[2017-12-06 16:38:01 INFO] Steady state hypothesis: Services are all available and healthy
[2017-12-06 16:38:01 INFO] Probe: all-services-are-healthy
[2017-12-06 16:38:01 INFO]   => succeeded with 'True'
[2017-12-06 16:38:01 INFO] Steady state hypothesis is met, we can carry on!
[2017-12-06 16:38:01 INFO] Action: stop-provider-service
[2017-12-06 16:38:01 INFO]   => succeeded without any result value
[2017-12-06 16:38:01 INFO]   Pausing after for 10s...
[2017-12-06 16:38:11 INFO] Probe: all-services-are-healthy
[2017-12-06 16:38:11 INFO]   => succeeded with 'True'
[2017-12-06 16:38:11 INFO] Probe: consumer-service-must-still-respond
[2017-12-06 16:38:24 ERROR]    => failed: {"timestamp":1512574703491,"status":500,"error":"Internal Server Error","exception":"feign.RetryableException","message":"connect timed out executing GET http://my-provider-service:8080/","path":"/invokeConsumedService"}
[2017-12-06 16:38:24 INFO] Experiment is now complete. Let's rollback...
[2017-12-06 16:38:24 INFO] No declared rollbacks, let's move on.
[2017-12-06 16:38:24 INFO] Experiment is now completed
```

This new learning from the experiment invites us to learn how to overcome this
and, in our case, we'll do that using a fallback mechanism, like a circuit
breaker, in our consumer code.

## Running the Experiment to Gain Confidence that the `before` Weaknesses have been Overcome

The services deployed as part of the `03-after` directory have incorporated a
circuit breaker for just this newly discovered weakness. Now you can deploy
this new, improved system and re-run the experiment:

```shell
$ kubectl delete deployment my-consumer-app my-provider-app
$ kubectl create -f 03-after/provider-deployment.json
$ kubectl create -f 03-after/consumer-deployment.json
```

You can re-run the experiment with the Chaos Toolkit CLI:

```shell
(venv) $ chaos run experiment.json
```

Now the experiment should complete successfully and report general system
steady-state health according to the experiment's probes as shown in the
following experiment sample output:

```shell
[2017-12-06 16:42:58 INFO] Validating experiment's syntax
[2017-12-06 16:42:58 INFO] Experiment looks valid
[2017-12-06 16:42:58 INFO] Running experiment: System is resilient to provider's failures
[2017-12-06 16:42:58 INFO] Steady state hypothesis: Services are all available and healthy
[2017-12-06 16:42:58 INFO] Probe: all-services-are-healthy
[2017-12-06 16:42:58 INFO]   => succeeded with 'True'
[2017-12-06 16:42:58 INFO] Steady state hypothesis is met, we can carry on!
[2017-12-06 16:42:58 INFO] Action: stop-provider-service
[2017-12-06 16:42:58 INFO]   => succeeded without any result value
[2017-12-06 16:42:58 INFO]   Pausing after for 10s...
[2017-12-06 16:43:08 INFO] Probe: all-services-are-healthy
[2017-12-06 16:43:08 INFO]   => succeeded with 'True'
[2017-12-06 16:43:08 INFO] Probe: consumer-service-must-still-respond
[2017-12-06 16:43:18 INFO]   => succeeded with 'Hmm, no one available to say hello just yet ... maybe try later?'
[2017-12-06 16:43:18 INFO] Experiment is now complete. Let's rollback...
[2017-12-06 16:43:18 INFO] No declared rollbacks, let's move on.
[2017-12-06 16:43:18 INFO] Experiment is now completed
```
