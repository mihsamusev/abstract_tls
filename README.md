# sumotllab

Welcome to sumotllab - a SUMO based simulation environment to test and implement your traffic control algorithms.

[use this CircleCI example for documentation](https://circleci.com/docs/2.0/configuration-reference/)

## Table of Contents
1. [TLS Description](#paragraph1)

## Supported types of run

One network, one set of tls, N runs


## Installation
- SUMO
- strategoutils
- confuse

## Separation of tasks 

[extend_framework](/docs/extend_framework.md)




## Limitations / Details
- Single node intersections, no clusters
- No communications between TLS
- Will use last loaded traffic lights program, either initial or by `*.tll.xml`