## TLS description <a name="paragraph1"></a>
```yml
id: # existence of ID not validated
controller: # validated
constants:
    - MIN_TIME: 15
variables: # data used for decision making that can update every step, store MPC 
extract:
    user_data:
        - user_data_extraction_query_1:
        ...
        - user_data_extraction_query_n:
    tls_data:
        - tls_data_extraction_query_1:
        ...
        - tls_data_extraction_query_m:
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
        user_data:
		    - feature: count
		    user_type: pedestrian
			at: phase
			mapping:
				2: "ped_count" 
```

## Feature extraction queries

It is possible to extract both user_data as well as the traffic light data
```
```

### User data

```yml
user_data:
    - feature:    # can be [count, speed, eta, waiting_time]
	user_type:  # can be [pedestrian, cyclist, vehicle type]
  at:       # can be [lane, phase or detector]
  mapping:    # dict of mapping between "at" types to dict keys for output
    sumo_name_1: "variable_name_1"
    ...
    sumo_name_n: "variable_name_n"
```

for example, collect all pedestrians served during phases 0 and 1 of a tls

```yml
user_data:
    - feature: 'count'
	user_type: 'pedestrian'
	at: 'phase'
	mapping:
    0: 'p0'
    1: 'p1'
```

### tls_data
```yml
tls_data:
	- feature: elapsed_time # can be []
		to_var: x

```


### Using the feature extraction pipeline
If a query is provided to the TLS controller one can leverage
the `data_pipeline` class and the `extract()` method to 

```python
def calculate_next_phase()
	self.variables = self.data_pipeline.extract()

```
