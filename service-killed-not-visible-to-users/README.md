
# "Randomly Killed Service Not Visible To Users" Sample Chaos Experiment

This sample experiment demonstrates a simple learning loop where the `before`
conditions are such that the  services don't use circuit breakers and so
undesirable weaknesses will be exposed, and the `after` conditions are such
that same experiment will now not raise the same concerns once something like a
circuit breaker has been introduced.

## Prerequisites

To run this you will need the [Chaos Toolkit CLI][chaos-toolkit] >= 0.4.0
installed and have access to a Kubernetes cluster. For simplicity in getting
up and running we assume you're using a local [minikube][] here. You also need
an account with [Gremlin][gremlin] and a token to run attacks.

[minikube]: https://kubernetes.io/docs/getting-started-guides/minikube/
[gremlin]: https://www.gremlin.com
[chaos-toolkit]: https://github.com/chaostoolkit/chaostoolkit

### Chaos Toolkit Dependencies

Make sure to install the latest chaostoolkit CLI:

```shell
(venv) $ pip install -U chaostoolkit
```

You will also need to install the [chaostoolkit-kubernetes][chaosk8s] and
[chaostoolkit-gremlin][chaosgremlin] extensions:

```shell
(venv) $ pip install -U chaostoolkit-kubernetes chaostoolkit-gremlin
```

[chaosk8s]: https://github.com/chaostoolkit/chaostoolkit-kubernetes
[chaosgremlin: https://github.com/chaostoolkit/chaostoolkit-gremlin

### Kubernetes

If you running minikube, you may want to create your stack as follows:

```
$ minikube delete
$ minikube start --cpus=2 --memory=2048
```

If not, make sure either you have the Kubernetes config under `~/kube` or
amend the experiment file to add secrets with the appropriate credentials.
See the [chaostoolkit-kubernetes][chaosk8s] extension.

### Gremlin

You will need to set three environment variables:

```
export GREMLIN_EMAIL=your email
export GREMLIN_PWD=your password
export GREMLIN_ORG_NAME=the org name of your user
```

It is a good idea to add those values in a file you can source.

```
$ chmod 600 ~/.gremlin
$ source ~/.gremlin
```

Then, you will need to update the `gremlin.yml` Kubernetes spec with the
Gremlin org and secret ID that were given to you when you registered to Gremlin.

Next, you can deploy Gremlin in your cluster as follows:

```
$ kubectl -f gremlin.yml
```

Make sure it is running by looking for it:

```
$ kubectl --namespace=kube-system logs gremlin
```

## Running the Experiment to Discover the `before` Weaknesses

Once you have the prerequisites in place you can deploy the `before` conditions
of the application as follows:

```shell
$ kubectl create -f consumer-service.json -f provider-service.json -f 01-before/
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
$ chaos --log-file=experiment.log run experiment.json 
[2017-12-12 17:32:04 INFO] Validating experiment's syntax
[2017-12-12 17:32:05 INFO] Experiment looks valid
[2017-12-12 17:32:05 INFO] Running experiment: System is resilient to provider's failures
[2017-12-12 17:32:05 INFO] Steady state hypothesis: Services are all available and healthy
[2017-12-12 17:32:05 INFO] Probe: all-services-are-healthy
[2017-12-12 17:32:05 INFO] Probe: provider-is-available
[2017-12-12 17:32:05 INFO] Steady state hypothesis is met, we can carry on!
[2017-12-12 17:32:05 INFO] Action: kill-provider-microservice
[2017-12-12 17:32:07 INFO] Probe: provider-should-be-in-a-broken-state
[2017-12-12 17:32:22 INFO] Probe: consumer-service-must-still-respond
[2017-12-12 17:33:02 ERROR]   => failed: activity took too long to complete
[2017-12-12 17:33:02 INFO] Probe: provider-is-back-to-a-healthy-state
[2017-12-12 17:33:02 INFO]   Pausing before activity for 30s...
[2017-12-12 17:33:32 INFO] Probe: all-services-are-healthy
[2017-12-12 17:33:32 INFO] Experiment is now complete. Let's rollback...
[2017-12-12 17:33:32 INFO] No declared rollbacks, let's move on.
[2017-12-12 17:33:32 INFO] Experiment is now completed
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
$ kubectl create -f 03-after/
```

You can re-run the experiment with the Chaos Toolkit CLI:

```shell
(venv) $ chaos run experiment.json
```

Now the experiment should complete successfully and report general system
steady-state health according to the experiment's probes as shown in the
following experiment sample output:

```shell
$ chaos --log-file=experiment.log run experiment.json 
[2017-12-12 17:38:14 INFO] Validating experiment's syntax
[2017-12-12 17:38:14 INFO] Experiment looks valid
[2017-12-12 17:38:14 INFO] Running experiment: System is resilient to provider's failures
[2017-12-12 17:38:14 INFO] Steady state hypothesis: Services are all available and healthy
[2017-12-12 17:38:14 INFO] Probe: all-services-are-healthy
[2017-12-12 17:38:14 INFO] Probe: provider-is-available
[2017-12-12 17:38:14 INFO] Steady state hypothesis is met, we can carry on!
[2017-12-12 17:38:14 INFO] Action: kill-provider-microservice
[2017-12-12 17:38:16 INFO] Probe: provider-should-be-in-a-broken-state
[2017-12-12 17:38:31 INFO] Probe: consumer-service-must-still-respond
[2017-12-12 17:38:37 INFO] Probe: provider-is-back-to-a-healthy-state
[2017-12-12 17:38:37 INFO]   Pausing before activity for 30s...
[2017-12-12 17:39:07 INFO] Probe: all-services-are-healthy
[2017-12-12 17:39:07 INFO] Experiment is now complete. Let's rollback...
[2017-12-12 17:39:07 INFO] No declared rollbacks, let's move on.
[2017-12-12 17:39:07 INFO] Experiment is now completed
```

## Clean Up

You should probably delete the Kubernetes cluster:

```
$ kubectl delete svc my-consumer-service my-provider-service
$ kubectl delete deployment my-consumer-app my-provider-app

```

You can even simply delete the Kubernetes cluster when it's a throwaway one:

```
$ minikube delete
```