
# "Service Down Not Visible To Users" Sample Chaos Experiment

This sample experiment demonstrates a simple learning loop where the `before`
conditions are such that the  services don't use circuit breakers and so
nundesirable weaknesses will be exposed, and the `after` conditions are such
that same experiment will now not raise the same concerns once something like a
circuit breaker has been introduced.

More will be coming soon how Chaos Experiments help you achieve double-loop
learning in the main Chaos Toolkit documentation.

## Prerequisites

To run this you will need the [Chaos Toolkit CLI][chaos-toolkit] installed and
have access to a Kubernetes cluster. For simplicity in getting up and running we
assume you're using a local [minikube][] here.

[chaos-toolkit]: https://github.com/chaostoolkit/chaostoolkit
[minikube]: https://kubernetes.io/docs/getting-started-guides/minikube/

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
(venv) $ pip install chaostoolkit-kubernetes
(venv) $ chaos run experiment.json
```

The experiment will highlight a weakness in that the consumer endpoint failed
to reply when this is what we would expect even when the producer has failed as
shown in the following experiment sample output:

```shell
[2017-10-06 17:37:33 INFO] Running experiment: System is resilient to provider's failures
[2017-10-06 17:37:33 INFO] Observing steady state: All services must be healthy before we begin
[2017-10-06 17:37:33 INFO] Steady State suceeeded
[2017-10-06 17:37:33 INFO] Observing steady state: Before we kill it, our microservice should be alive
[2017-10-06 17:37:33 INFO] Steady State suceeeded
[2017-10-06 17:37:33 INFO] Observing action: Let's stop our provider
[2017-10-06 17:37:33 INFO] Action suceeeded
[2017-10-06 17:37:33 INFO] Observing close state: All services must be healthy before we begin
[2017-10-06 17:37:33 INFO] Close State suceeeded
[2017-10-06 17:37:33 INFO] Observing steady state: Consume should respond as if nothing
[2017-10-06 17:37:44 ERROR] Steady State failed: {"timestamp":1507304264100,"status":500,"error":"Internal Server Error","exception":"feign.RetryableException","message":"connect timed out executing GET http://my-provider-service:8080/","path":"/invokeConsumedService"}
[2017-10-06 17:37:44 INFO] Experiment is now complete
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
[2017-10-06 17:40:25 INFO] Running experiment: System is resilient to provider's failures
[2017-10-06 17:40:25 INFO] Observing steady state: All services must be healthy before we begin
[2017-10-06 17:40:25 INFO] Steady State suceeeded
[2017-10-06 17:40:25 INFO] Observing steady state: Before we kill it, our microservice should be alive
[2017-10-06 17:40:26 INFO] Steady State suceeeded
[2017-10-06 17:40:26 INFO] Observing action: Let's stop our provider
[2017-10-06 17:40:26 INFO] Action suceeeded
[2017-10-06 17:40:26 INFO] Observing close state: All services must be healthy before we begin
[2017-10-06 17:40:26 INFO] Close State suceeeded
[2017-10-06 17:40:26 INFO] Observing steady state: Consume should respond as if nothing
[2017-10-06 17:40:30 INFO] Steady State suceeeded
[2017-10-06 17:40:30 INFO] Experiment is now complete
```
