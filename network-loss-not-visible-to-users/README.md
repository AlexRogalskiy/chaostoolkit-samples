
# "Network Loss Not Visible To Users" Sample Chaos Experiment

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
[2017-10-23 15:29:46 INFO] Experiment: System is resilient to network link loss
[2017-10-23 15:29:46 INFO] Step: Our microservices are expected to be available for this experiment
[2017-10-23 15:29:46 INFO]   Steady State: Looking up the availability of our services
[2017-10-23 15:29:46 INFO]   => succeeded with 'None'
[2017-10-23 15:29:46 INFO] Step: Service endpoints must be initialized so we know microservices can talk to each other
[2017-10-23 15:29:46 INFO]   Steady State: Check provider service is initialized
[2017-10-23 15:29:46 INFO]   => succeeded with 'None'
[2017-10-23 15:29:46 INFO] Step: Pretend network is broken between consumer and provider by killing the provider service endpoint
[2017-10-23 15:29:46 INFO]   Action: Remove the provider service endpoint
[2017-10-23 15:29:46 INFO]   => succeeded with 'None'
[2017-10-23 15:29:46 INFO] Step: Consumer should not be impacted by provider's failure
[2017-10-23 15:29:46 INFO]   Steady State: Consume should respond as if nothing, even if it's a message saying try later
[2017-10-23 15:29:56 ERROR]    => failed: {"timestamp":1508765398139,"status":500,"error":"Internal Server Error","exception":"feign.RetryableException","message":"my-provider-service executing GET http://my-provider-service:8080/","path":"/invokeConsumedService"}
[2017-10-23 15:29:56 INFO] Experiment is now complete
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
$ kubectl create -f provider-service.json
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
[2017-10-23 15:35:33 INFO] Experiment: System is resilient to network link loss
[2017-10-23 15:35:33 INFO] Step: Our microservices are expected to be available for this experiment
[2017-10-23 15:35:33 INFO]   Steady State: Looking up the availability of our services
[2017-10-23 15:35:33 INFO]   => succeeded with 'None'
[2017-10-23 15:35:33 INFO] Step: Service endpoints must be initialized so we know microservices can talk to each other
[2017-10-23 15:35:33 INFO]   Steady State: Check provider service is initialized
[2017-10-23 15:35:33 INFO]   => succeeded with 'None'
[2017-10-23 15:35:33 INFO] Step: Pretend network is broken between consumer and provider by killing the provider service endpoint
[2017-10-23 15:35:33 INFO]   Action: Remove the provider service endpoint
[2017-10-23 15:35:33 INFO]   => succeeded with 'None'
[2017-10-23 15:35:33 INFO] Step: Consumer should not be impacted by provider's failure
[2017-10-23 15:35:33 INFO]   Steady State: Consume should respond as if nothing, even if it's a message saying try later
[2017-10-23 15:35:42 INFO]   => succeeded with 'Hmm, no one available to say hello just yet ... maybe try later?'
[2017-10-23 15:35:42 INFO] Experiment is now complete
```
