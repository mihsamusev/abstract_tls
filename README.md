# sumotllab

Welcome to `sumotllab` - a SUMO based simulation environment to implement and benchmark your traffic control algorithms.

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

## Getting started
### Installing the project repository
```sh
git clone https://github.com/mihsamusev/sumotlslab.git
```

### Installing dependencies
Recommended to create `conda` environment from provided configuration file.
```sh
conda env create -f environment.yml
conda activate sumotlslab
```

### Installing SUMO
Coming soon


### Documentation
1. [Run configuration file](docs/run_configuration.md)
2. [Adding your own controllers](docs/extend_framework.md)
3. [Examples](docs/examples.md)

## Agent Zoo
Coming soon

## Limitations / Details
- Single node intersections, no clusters
- No communications between TLS
- Will use last loaded traffic lights program, either initial or by `*.tll.xml`