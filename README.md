trying to abstract controllers for SUMO controlller benchmarks




Demand is generated using `randomTrips.py`

For vehicles - binomial with `n = 5` and `p = peirod / 5 = 1/5`

```sh
python $SUMO_HOME/tools/randomTrips.py \
    -n data/block.net.xml \
    --weights-prefix data/edge_weights \
    -o data/vehicles.rou.xml \
    --seed 42 \
    --validate \
    -b 0 \
    -e 3000 \
    --binomial 5
```

For pedestrians - uniform every 5s
```sh
python $SUMO_HOME/tools/randomTrips.py \
    -n data/block.net.xml \
    -o data/pedestrians.rou.xml \
    --pedestrians \
    --max-distance 100 \
    --period 5 
```

## TLS description
```yml
id:
controller:
    class:
    module: # if blank then will search in base folder for controllers
    constants:
        - MIN_TIME: 15
    variables:
    extract:
        - feature_extraction_query_1:
        ...
        - feature_extraction_query_2:
```

For example

```yml
id:
controller:
    class: CrosswalkTLS
    constants:
        MIN_TIME: 15
    variables:
        ped_count: 0
    extract:
        - feature: count
        user_type: pedestrian
        from: phase
        map:
            2: "ped_count" 
```

## Feature extraction queries

```yml
feature:    # can be [count, speed, eta, waiting_time]
user_type:  # can be [pedestrian, cyclist, vehicle type]
from:       # can be [lane, phase or detector]
mapping:    # dict of mapping between from types to dict keys for output
    from_1: "to_1"
    ...
    from_n: "to_n"
```

for example, collect all pedestrians served during phases 0 and 1 of a tls

```yml
feature: 'count'
user_type: 'pedestrian'
from: 'phase'
mapping:
    0: 'p0'
    1: 'p1'
```

```python
from feature_extraction import FeaturePipeline

fe = FeaturePipeline(tls_id='A1', extract)

for s in simulation_steps:
    update_sumo()
    state = fe.extract()
    do_smth_awesome_with(state)
```

## Limitations
Single node intersections, no clusters