# Table of Contents
1. [TLS Description](#paragraph1)


## Demand generation

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

## Separation of tasks 

Concrete TLSAgent implementation:
 - Sumbclass TLSAgent and implement `calclulate_next_phase()` method
 - Register the agent using `TLSFactory.register_agent(<agent_name>)`
 - 

Config manager ensures:
 - existence of compulsory configuration fields
 - valid formats, existsing file paths and executables are put in
 - recognition of your custom TLSAgent as a valid controller method


## TLS description <a name="paragraph1"></a>
```yml
id:
controller:
    class:
    module: # if blank then will search in base folder for controllers
    constants:
        - MIN_TIME: 15
    variables: # data used for decision making that can update every step, store MPC 
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

It is possible to extract both user_data as well as the traffic light data
```
```

### User data
```yml
user_data:
-	feature:    # can be [count, speed, eta, waiting_time]
	user_type:  # can be [pedestrian, cyclist, vehicle type]
  from:       # can be [lane, phase or detector]
  mapping:    # dict of mapping between from types to dict keys for output
    from_1: "to_1"
    ...
    from_n: "to_n"
```

for example, collect all pedestrians served during phases 0 and 1 of a tls

```yml
-	feature: 'count'
	user_type: 'pedestrian'
	from: 'phase'
	mapping:
			0: 'p0'
			1: 'p1'
```

### Using the feature extraction pipeline
If a query is provided to the TLS controller one can leverage
the `data_pipeline` class and the `extract()` method to 
```python

def calculate_next_phase()
		self.variables = self.data_pipeline.extract()


```

## Limitations
Single node intersections, no clusters