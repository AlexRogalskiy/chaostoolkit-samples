# Welcome to the Chaos Toolkit Samples

Within this project there are a number of samples that aim to demonstrate how Chaos Engineering experiments can be constructed and executed to build confidence that weaknesses are not present in a microservice-based system.

The full catalogue of samples include:
* [Service Down Not Visible To Users][service-down] - Where an experiment is executed that highlights a weakness with a dead service dependency and this is then learned from and a circuit breaker is applied to overcome this discovered weakness.
* [Memory Resource Exhaustion Not Visible To Users][memory-exhaustion] - Where an experiment is executed that highlights a memory resource weakness in a service dependency and this is then learned from and a circuit breaker is applied to overcome this discovered weakness.
* [Processor Resource Exhaustion Not Visible To Users][processor-exhaustion] - Where an experiment is executed that highlights a processing resource weakness in a service dependency and this is then learned from and a circuit breaker is applied to overcome this discovered weakness.
* [Network Loss Not Visible To Users][network-loss] - Where an experiment is executed that highlights a service dependency weakness when the interconnecting network is lost between the services and this is then learned from and a circuit breaker is applied to overcome this discovered weakness.

[service-down]: https://github.com/chaostoolkit/chaostoolkit-samples/tree/master/service-down-not-visible-to-users
[memory-exhaustion]: https://github.com/chaostoolkit/chaostoolkit-samples/tree/master/memory-resource-exhaustion-not-visible-to-users
[processor-exhaustion]: https://github.com/chaostoolkit/chaostoolkit-samples/tree/master/processor-resource-exhaustion-not-visible-to-users
[network-loss]: https://github.com/chaostoolkit/chaostoolkit-samples/tree/master/network-loss-not-visible-to-users