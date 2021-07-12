<style>
  table {margin-left: 0 !important;}
</style>

# Run configurations
The simulation task for `runner.py` is specified inside a `*.yml` configuration file. In the following the building blocks of such configuration file are described. An example of a configuration file can be found in [`configs/example_block.yml`](configs/example_block.yml). The general structure of all configurations includes following fields.

| Key | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `job`     | Yes  | Map | Parameters defining the job. |
| `sumo`    | Yes  | Map | Parameters defining inputs to SUMO simulator. |
| `tls`     | Yes  | Map | Parameters defining the agents controlling SUMO traffic lights. |
| `logging` | No   | Map | Parameters defining the output logging. |

## `job`
The `job` field defines the run name and its base directory.

| Key | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `name`   | Yes | String | Run name. |
| `dir`    | No  | String | Valid base directory for the project files such as SUMO network / demand, additional files for controllers, output logs. Default: the directory of the `runner.py` |

**Example**:
We would like to configure a run named `latest` whos content resides in `examples/block/` directory.
```yml
job:
  name: latest
  dir: examples/block
```


## `sumo`
The sumo field defines the path to necessary sumo simulation files and parameters.
| Key | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `dir`       | Yes| String | Directory of the SUMO files relative to `job.dir`. |
| `network`   | Yes| String | SUMO network file name relative to `sumo.dir`.|
| `route`     | Yes| List   | List of SUMO route / demand files relative to `sumo.dir`.|
| `gui`       | No | Bool   | Whether to visualize simulation in GUI. Default = True. |
| `max_steps` | No | Int    | Maximum number of steps in the simulation. Default = 10e5. |
| `additional`| No | List   | List of additional files such as [detector definitions](https://sumo.dlr.de/docs/Simulation/Output/#simulated_detectors) or [traffic light programs](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html#defining_new_tls-programs) relative to `sumo.dir`.|

**Example**:
We would like run a simulation on a `block.net.xml` network with `vehicle.rou.xml` demand, and visualize results in GUI. We give our own traffic light and detector definitions in the additional files. All files reside in `sumo/` directory relative to the base project directory `job.dir`.

```yml
sumo:
  dir: "sumo"
  gui: True
  network: block.net.xml
  additional: [tll.add.xml, det.add.xml]
  route: [vehicles.rou.xml]
```

## `tls[*]`

The `tls` field allows to specify a list of nodes controlled by agents together with the constants and variables used to take the control decisions. Each of the `tls` entries has following fields.

| Key | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id`       | Yes| String | List of SUMO network node IDs controlled by the agent.|
| `controller`| Yes| String | Controller name that is registered under `tlsagents/` directories. |
| `constants` | No | Map | Key / value pairs describing constants that controller is initialized with. The application of the constants is up to the concrete controller impelmentation. |
| `variables` | No | Map | Key / value pairs describing variables that the controller updates every simulation step. The variables are populated  The application of the variables is up to the concrete controller impelmentation. |
| `extract`   | No | Map | Data extraction query that describes which road users to register and to which variables to write the results. More in [tls[*].extract](#tls[*].extract). |

**Example**: Definition of 2 controllers, a timed controller at A1 and a pedestrian responsive controller at B1. The B1 controller extracts the count of pedestrians served at phase 2 of its SUMO `tlLogic` program definition and writes it to the `ped_count` variable. The logic of how `base_crosswalk` calculates a new phase given the inputs is defined in [`tlsagents/base.py`](`../tlsagents/base.py`).
```yml
tls:
  - id: A1
    controller: base_timed

  - id: B1
    controller: base_crosswalk
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
### `tls[*].extract`
### `tls[*].extract.user_data`

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

### `tls[*].extract.traffic_data`
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

## `logging`
The `logging` field is an optional field that specifies the ids of the agents to be logged and types of information that has to be logged.

| Key | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `ids`         | Yes| List | List of SUMO network node IDs controlled by the agent. |
| `data`        | Yes| List | Should be one of `objectives`, `variables`, `states`|
| `to_file`     | No | Boll | Whether to print log to file. The name is assembled from config as `<job.dir>/output/<job.name>_<logging.timestamped>.log`. Default = False |
| `to_console`  | No | Bool | Whether to print log to console every simulation step. Default = True | 
| `timestamped` | No | Bool | Whether to include simulation start time in the name of the log file. Default = False |

**Example**:
We would like to log the states and variables of an agent sitting at note A1 to a timestamped file.

```yml
logging:
  ids: [A1]
  data: [state, variables]
  to_file: True
  timestamped: True
```

### `logging.data`
The `logging.data` field affects what data will be displayed / saved during logging.

- `objectives` - `dict` with results of objective function evaluation at current timestep when doing optimal control. Implemented in `TLSAgent.get_objectives()` and is `{}` by default since base controller does not rely on optimization.
- `variables` - `dict` with variables, aka, time varying inputs about road users registered at the controlled node. Implemented in `TLSAgent.get_variables()` and is `{}` by default since base controller does not register road users.
- `states` - `dict` with current steps phase and elapsed time . Implemented in `TLSAgent.get_states()`.

