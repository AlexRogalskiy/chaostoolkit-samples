
# Sample Chaos Experiment - `service-down-not-visible-to-users` 

This sample experiment demonstrates a simple learning loop where the `before` conditions are such that the 
services don't use circuit breakers and sonundesirable failures will be exposed, and the
`after` conditions are such that same experiment will now not raise the same concerns once something like a circuit breaker has been introduced.

More will be coming soon how Chaos Experiments help you achieve double-loop learning in the main Chaos Toolkit documentation.

## Prerequisites

To run this you will need the [Chaos Toolkit CLI][chaos-toolkit] installed and have access to
a Kubernetes cluster. Instead of installing the Chaos Toolkit CLI directly you can execute the CLI using [Docker][docker]. For simplicity in getting up and running we assume you're using a local [minikube][] here.

[chaos-toolkit]: https://github.com/chaostoolkit/chaostoolkit
[minikube]: https://kubernetes.io/docs/getting-started-guides/minikube/
[docker]: https://www.docker.com/

## Running the Experiment to Discover the `before` Weaknesses

Once you have the prerequisites in place you can deploy the `before` conditions of the application as follows:

```shell
$ kubectl create -f consumer-service.json
$ kubectl create -f provider-service.json
$ kubectl create -f 01-before/provider-deployment.json
$ kubectl create -f 01-before/consumer-deployment.json
``` 

Once the deployments have settled you need to make a note of the URL at which you can now reach
the consumer service. If you are running minikube you can find this URL using the following command:

```shell
$ minikube service my-consumer-service --url
```

With the URL in hand you can now edit the `experiment.json` file towards the end to set the URL for the
last probe in the experiment.

To run the experiment against the `before` conditions you can either use the Chaos Toolkit CLI directly:

```shell
(venv) $ chaos run experiment.json
```

Or use the packaged Docker image that does make the assumption that you are using minikube and running from
the directory that this README file is contained within:

```shell
$ docker run --rm -it \
    -v $HOME/.kube:/root/.kube \
    -v $HOME/.minikube:$HOME/.minikube \
    -v `pwd`:/tmp/exp \
    chaostoolkit/chaostoolkit run /tmp/exp/experiment.json
```

The experiment will highlight a weakness in that the consumer endpoint failed to reply
when this is what we would expect even when the producer has failed as shown in the following experiment sample output:

```shell
[I 170930 14:07:02 plan:27] Executing plan '/tmp/exp/experiment.json'
[I 170930 14:07:02 plan:66] Loading plan...
[I 170930 14:07:02 __init__:43] Loading the following target layers:
[I 170930 14:07:02 __init__:49]  platforms: kubernetes => chaostoolkit.layers.platforms.k8s
[I 170930 14:07:02 __init__:49]  applications: spring => chaostoolkit.layers.applications.spring
[I 170930 14:07:02 plan:96] Running plan: 'System is resilient to provider's failures'
[I 170930 14:07:02 plan:104] Moving on to step 'Checking our system is healthy'
[I 170930 14:07:02 plan:134]  Applying steady probe 'microservices-all-healthy'
[E 170930 14:07:02 report:23] the system is unhealthy
```

This new learning from the experiment invites us to learn how to overcome this and, in our case, we'll do that using a fallback mechanism, like a circuit breaker, in our
consumer code.

## Running the Experiment to Gain Confidence that the `before` Weaknesses have been Overcome

The services deployed as part of the `03-after` directory have incorporated a circuit breaker for just this newly discovered weakness. Now you can deploy this new, improved system and re-run the experiment:

```shell
$ kubectl delete deployment my-consumer-app my-provider-app
$ kubectl create -f 03-after/provider-deployment.json
$ kubectl create -f 03-after/consumer-deployment.json
```

You can re-run the experiment with the Chaos Toolkit CLI directly:

```shell
(venv) $ chaos run experiment.json
```

Or using the Docker image again:

```shell
$ docker run --rm -it \
    -v $HOME/.kube:/root/.kube \
    -v $HOME/.minikube:$HOME/.minikube \
    -v `pwd`:/tmp/exp \
    chaostoolkit/chaostoolkit run /tmp/exp/experiment.json
```

Now the experiment should complete successfully and report general system steady-state health according to the experiment's probes as shown in the following experiment sample output:

```shell
[I 170930 14:12:29 plan:27] Executing plan '/tmp/exp/experiment.json'
[I 170930 14:12:29 plan:66] Loading plan...
[I 170930 14:12:29 __init__:43] Loading the following target layers:
[I 170930 14:12:29 __init__:49]  platforms: kubernetes => chaostoolkit.layers.platforms.k8s
[I 170930 14:12:29 __init__:49]  applications: spring => chaostoolkit.layers.applications.spring
[I 170930 14:12:29 plan:96] Running plan: 'System is resilient to provider's failures'
[I 170930 14:12:29 plan:104] Moving on to step 'Checking our system is healthy'
[I 170930 14:12:29 plan:134]  Applying steady probe 'microservices-all-healthy'
[I 170930 14:12:29 plan:104] Moving on to step 'Killing the provider abruptly'
[I 170930 14:12:29 plan:134]  Applying steady probe 'microservice-available-and-healthy'
[I 170930 14:12:29 plan:183]  Executing action 'kill-microservice'
[I 170930 14:12:30 plan:198]  Pausing 10s
[I 170930 14:12:40 plan:159]  Applying close probe 'microservice-is-not-available'
[I 170930 14:12:40 plan:104] Moving on to step 'Consumer should not be impacted by provider's failure'
[I 170930 14:12:40 plan:134]  Applying steady probe 'endpoint-should-respond-ok'
[I 170930 14:12:41 plan:110] Done with plan: 'System is resilient to provider's failures'
```
