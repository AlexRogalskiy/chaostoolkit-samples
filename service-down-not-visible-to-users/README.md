This experiment will show you how to learn that your service could benefit
from a fallback when one of its dependency fails.

To run this you will need the chaostoolkit CLI installed and have access to
a Kubernetes cluster. You can try for instance installing minikube.

Once those two requirements are in place, first deploy your application as
follows:

```
$ kubectl create -f consumer-service.json
$ kubectl create -f provider-service.json
$ kubectl create -f 01-before/provider-deployment.json
$ kubectl create -f 01-before/consumer-deployment.json
``` 

Once they have settled, make a note of the URL at which you can now reach
the consumer service. If you are running minikube, try this:

```
$ minikube service my-consumer-service --url
```

then edit the `experiment.json` file towards the end and set the URL at the
last probe.

Now you can run your experiment as follows:

```
(venv) $ chaos run experiment.json
```

This experiment should indicate that the consumer endpoint failed to reply
when this is what we would expect even when its producer has failed. This
invites us to use a fallback mechanism, like a circuit breaker, in our
consumer code.

This is what was done in the application under the `03-after` directory. Let's
deploy it and re-run our experiment:

```
$ kubectl create -f 03-after/provider-deployment.json
$ kubectl create -f 03-after/consumer-deployment.json
```

```
(venv) $ chaos run experiment.json
```

Now the experiment should go all the way successfully because our probe
asking the consumer's status was successful!
