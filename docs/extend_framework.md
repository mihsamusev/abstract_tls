# Implementing new controllers

## Prerequisites

In order to implement your own controller / agent and use it in the simulation user is asked to fullfil two conditions:

Concrete agent implementation:
- New agent shall be saved in a `*.py` file under `tlsagents` directory
- New agent shall iherit from `TLSAgent` and implement a custom `calculate_next_phase()` method
- New agent shall be registered using a decorator`TLSFactory.register_agent(<AGENT_NAME>)`

Configuration file:
 - Use `controller: <AGENT_NAME>` in the tls definition

## Example

Following example implements a controller that outputs a random phase each simulation step. Firstly create a python file under `tlsagents/` folder. Create a custom agent class that inherits from `TLSAgent`. In the `__init__` method describe specific application of `constants`, `variables`, `data_query` and `optimizer` if necessary. Then implement the `calculate_next_phase()` method that returns an integer id of the phase described in the current SUMO [`tlLogic`](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html#defining_new_tls-programs) that came eitther with the network `*.net.xml` file or as an additional [`*.add.xml`](https://sumo.dlr.de/docs/sumo.html#format_of_additional_files) file. Remember to register your agent with `@TLSFactory.register_agent` decorator as the config validation will return an error if the agent is not in the register.

```python
# tlsagents/custom_agents.py

from tlsagents.base import TLSAgent, TLSFactory
import random

@TLSFactory.register_agent('my_new_ctrl')
class OneWeirdTLS(TLSAgent):
    def __init__(self, tls_id, constants=None, variables=None,
        data_query=None, optimizer=None):
        super().__init__(tls_id, constants, variables, data_query, optimizer)

    def calculate_next_phase(self):
        return random.randint(0, self.n_phases-1)
```


```yml
# configs/custom_run.yml
...
tls:
    - id: A1
    controller: my_new_ctrl 
...
```

Running the simulation will result in the following visuals.
```bash
python runner.py -c configs/custom_run.yml
```

![random_controller](images/random_controller.gif)
