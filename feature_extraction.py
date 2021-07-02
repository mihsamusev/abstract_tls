import traci
import copy

def add_phase(state, target, tls_id, phase_map):
    """
    Extracts and inserts TLS phase with traci 
    to the state passed to Stratego
    """
    phase = traci.trafficlight.getPhase(tls_id)
    phase = phase_map.get(phase)
    if isinstance(state[target], list):
        state[target][phase] = 1
    else:
        state[target] = phase
    return state

def add_duration(state, target, tls_id):
    """
    Extracts and inserts TLS phase duration with traci 
    to the state passed to Stratego
    """
    duration = traci.trafficlight.getPhaseDuration(tls_id)
    state[target] = float(duration)
    return state

def add_queue(state, target, lane):
    """
    Extracts and inserts accumulated number of vehicles
    to the state passed to Stratego
    """
    number = traci.lane.getLastStepVehicleNumber(lane)
    if isinstance(target, list):
        key, idx = target
        state[key][idx] += number
    else:
        state[target] += number
    return state

def add_to_state(state, target, value):
    """
    Adds a value to state dictionary
    """
    if isinstance(target, list):
        key, idx = target
        state[key][idx] += value
    else:
        state[target] += value
    return state

def add_typed_lane_count(state, lane, target, user_type="DEFAULT_VEHTYPE"):
    """
    Extracts accumulated number of users from a lane and inserts
    to the state passed to Stratego
    """
    ids = traci.lane.getLastStepVehicleIDs(lane)
    number = sum([1 for i in ids if traci.vehicle.getTypeID(i) == user_type])
    state = add_to_state(state, target, number)
    return state

def add_typed_phase_count(state, tls_id, phase_id, target, user_type="DEFAULT_VEHTYPE"):
    """
    Extracts accumulated number of users served by tls phase and inserts
    to the state passed to Stratego
    """

    # if pedestrian requested just use tls function to get served count at phase_id,
    # otherwise, extract lanes enabled for the phase_id and reuse lane count fcn
    ctrl_links = traci.trafficlight.getControlledLinks(tls_id)
    phase_lights = traci.trafficlight.getAllProgramLogics(
        tls_id)[-1].getPhases()[phase_id].state

    phase_links = set(
        [lane[0] for lane, col in zip(ctrl_links, phase_lights) if col.lower() == 'g'])

    if user_type == "pedestrian":
        ped_edges = [e for e in traci.edge.getIDList() if e.startswith(f":{tls_id}_w")]
        phase_cross_edges = [link[1].rsplit("_", 1)[0] for link in phase_links if link[0].startswith(":")]
        
        number = 0
        for edge in ped_edges:
            peds = traci.edge.getLastStepPersonIDs(edge)
            # what?
            for ped in peds:
                if (traci.person.getWaitingTime(ped) >= 1 and 
                    traci.person.getNextEdge(ped) in phase_cross_edges):
                    number += 1
        state = add_to_state(state, target, number)
    else:
        lanes = set([lanes[0] for lanes in phase_links])
        for lane in lanes:
            state = add_typed_lane_count(state, lane, target, user_type)

    return state


class TLSDataPipeline:
    """
    Populates state with data about tls and lanes depending on
    the config requirements
    """
    def __init__(self, tls_id, tls_program_id, state_template, query):
        self.tls_program_id = tls_program_id
        self.tls_id = tls_id
        self.query = query
        self.state_template = copy.deepcopy(state_template)
        self.state = {}

        self.detectors = None
        self.controlled_lanes = traci.trafficlight.getControlledLanes(self.tls_id)
        self.walking_edges = [e for e in traci.edge.getIDList() if e.startswith(f":{self.tls_id}_w")]
        self.crossing_edges = [e for e in traci.edge.getIDList() if e.startswith(f":{self.tls_id}_c")]
        self.n_ped_signals = len(self.crossing_edges)

        self.validate_targets()

    def reset_state(self):
        self.state = copy.deepcopy(self.state_template)


    def validate_targets(self):
        """
        Check whether state template variables area available for writting 
        extracted simulation data
        """
        lane_ids = traci.lane.getIDList()
        phase_count = len(traci.trafficlight.getAllProgramLogics(
            self.tls_id)[self.tls_program_id].getPhases())

        for q in self.query:
            origin = q["from"]
            for sumo_var, target_var in q["mapping"].items():
                # validate origin
                if origin == "lane":
                    assert sumo_var in lane_ids, \
                        f"{sumo_var} is not a SUMO link"
                elif origin == "phase":
                    assert str(sumo_var).isdigit(), \
                        f"{sumo_var} is not correct to be TLS phase"
                    assert int(sumo_var) < phase_count, \
                        f"{sumo_var} is not a TLS phases"

                # validate target_var
                if isinstance(target_var, list):
                    assert target_var[0] in self.state_template.keys(), \
                    f"{target_var[0]} is not in target variables"
                    assert target_var[1] <= len(self.state_template[target_var[0]]), \
                        f"{target_var[0]} at {target_var[1]} is out of bounds of target variable"
                else:
                    assert target_var in self.state_template.keys(), \
                    f"{target_var} is not in target variables"

    def extract(self):
        self.reset_state()
        for q in self.query:
            if q["feature"] == "tls_state":
                raise NotImplementedError
            elif q["feature"] == "count":
                self.extract_counts(q["from"], q["user_type"], q["mapping"])
            elif q["feature"] == "speed":
                raise NotImplementedError
            elif q["feature"] == "eta":
                raise NotImplementedError
            elif q["feature"] == "waiting_time":
                raise NotImplementedError

        return self.state

    def extract_counts(self, origin, user_type, mapping):
        """
        Extracts and adds queue length of given vtype
        """
        if origin == "lane": 
            for lane, target_var in mapping.items():
                add_typed_lane_count(self.state, lane, target_var, user_type)
        elif origin == "detector":
            #for detector, target_var in mapping.items():
            NotImplementedError
        elif origin == "phase":
            for phase, target_var in mapping.items():
                add_typed_phase_count(
                    self.state, self.tls_id, phase, target_var, user_type)
