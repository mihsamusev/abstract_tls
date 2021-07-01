import copy
import traci


class TLSAgent:
	"""
	Abstract controller class
	"""
	def __init__(self, tls_id, constants=None, variables=None, feature_extractor=None, optimizer=None):
		"""
		:tls_id - 
		:variables - dict
		:feature_extractor
		:optimizer - object
		"""
		self.tls_id = tls_id
		self.phase = 0
		self.phase_list = traci.trafficlight.getAllProgramLogics(self.tls_id)[0].getPhases() # will break if pre-loaded tls
		self.n_phases = len(self.phase_list)
		self.elapsed = 0
		self.controlled_lanes = traci.trafficlight.getControlledLanes(self.tls_id)
		self.n_ped_signals = sum([1 for l in self.controlled_lanes if l.startswith(":")])

		self.walking_edges = [e for e in traci.edge.getIDList() if e.startswith(f":{self.tls_id}_w")]
		self.crossing_edges = [e for e in traci.edge.getIDList() if e.startswith(f":{self.tls_id}_c")]

		self.feature_extractor = feature_extractor
		self.optimizer = optimizer
		self.constants = constants
		self.variables = {}
		if variables:
			self.variables = copy.deepcopy(variables)

	def next_phase_id(self):
		"""
		calculate id of next phase
		"""
		next_phase = (self.phase + 1) % self.n_phases
		if len(self.phase_list[self.phase].next) > 0:
			next_phase = self.phase_list[self.phase].next[0]
		return next_phase

	def update_state(self):
		"""
		Here goes update logic using constants, variables, feature_extractor and optimizer
		"""
		raise NotImplementedError

	def get_state_dict(self):
		"""
		Return traffic signal state
		"""
		data = {
			"id": self.tls_id, 
			"phase": self.phase,
			"elapsed": self.elapsed
			}
		return data

	def get_variables(self):
		"""
		Returns variables
		"""
		return self.variables.copy()

class TimedTLS(TLSAgent):
	"""
	Controller class model wrapping a standart
	SUMO pre-timed controller
	"""
	def __init__(self, tls_id, constants=None, variables=None, feature_extractor=None, optimizer=None):
		super().__init__(tls_id, constants, variables, feature_extractor, optimizer)

	def update_state(self):
		"""
		Phases variables just follow tls logic, 
		so setting with traci is not necessary
		"""
		dt = traci.trafficlight.getNextSwitch(self.tls_id) - traci.simulation.getTime()
		if int(dt) == 0:
			self.phase = self.next_phase_id()
			self.elapsed = 0
		else:
			self.elapsed += 1


class RecordedTLS(TLSAgent):
	"""
	Controller class to replicated recorded sequence
	from a controller log
	"""
	def __init__(self, tls_id, constants, variables=None, feature_extractor=None, optimizer=None):
		super().__init__(tls_id, constants, variables, feature_extractor, optimizer)
		self.idx = 0
		self.phase = self.constants[self.idx]["phase"]
		self.phase_sequence = self.constants

	def update_state(self):
		"""
		Updates the state depending on the loaded variables sequence
		"""
		if self.constants[self.idx]["duration"] == self.elapsed:
			self.idx += 1
			self.phase = self.variables[self.idx]["phase"]
			self.elapsed = 0
			traci.trafficlight.setPhase(self.tls_id, self.phase)
		else:
			self.elapsed += 1


class CrosswalkTLS(TimedTLS):
	"""
	Controller class for a pedestrian responsive crosswalk controller
	"""
	def __init__(self, tls_id, constants, variables, feature_extractor=None, optimizer=None):
		super().__init__(tls_id, constants, variables, feature_extractor, optimizer)

		self.veh_phase_id = self.constants.get("veh_phase_id")
		if self.veh_phase_id is None:
			self.veh_phase_id = [
				i for i, p in enumerate(self.phase_list) if p.state.lower()[0]=='g'][0]

		self.min_green = self.constants.get("MIN_GREEN")
		if self.min_green is None:
			self.min_green = 15

		self.is_requested = False
		self.ped_key = list(self.variables)[0]

	def update_state(self):
		# read state
		self.variables = self.feature_extractor.extract()


		# during vehicle phase, see if request is sent
		if self.phase == self.veh_phase_id:
			self.is_requested = self.variables[self.ped_key] > 0
			self.elapsed += 1

			if self.elapsed > self.min_green and self.is_requested:
				self.phase = self.next_phase_id()
				traci.trafficlight.setPhase(self.tls_id, self.phase)
				self.elapsed = 0
				self.is_requested = False
	
		# otherwise run normally
		else:
			super().update_state()
			self.is_requested = False