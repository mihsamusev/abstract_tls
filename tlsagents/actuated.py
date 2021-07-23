from tlsagents.base import TLSFactory, TimedTLS

@TLSFactory.register_agent('actuated_two_phase')
class ActuatedTLS(TimedTLS):
	"""
	Controller class for a pedestrian responsive 2 phase controller
	"""
	def __init__(self, tls_id, constants=None, variables=None, data_query=None, optimizer=None):
		super().__init__(tls_id, constants, variables, data_query, optimizer)
		
		self.n_movement_phases = self.constants["n_movement_phases"]
		self.decision_phases = self.constants["decision_phases"]
		self.next_ped = self.constants["next_ped"]
		self.next_no_ped = self.constants["next_no_ped"]

		self.var_key = list(self.variables)[0]
		self.is_requested = [False, False]

		self.transitions = self.get_transitions_list()

	def get_transitions_list(self):
		"""
		Calculate transitions from
		"""
		transitions = []
		for p in self.phase_list[self.n_movement_phases:]:
			i, j = map(int, p.name.strip("( )").split(","))
			transitions.append((i, j))
		return transitions

	def get_transition(self, next_phase):
		if self.phase != next_phase:
			transition_phase = self.transitions.index((self.phase, next_phase))
			next_phase = self.n_movement_phases + transition_phase
		return next_phase

	def calculate_next_phase(self):
		next_phase = self.phase

		# read state
		self.variables = self.data_pipeline.extract()

		# remember request
		if self.is_switch_time() and self.phase in self.decision_phases:
			phase_idx = self.decision_phases.index(next_phase)
			self.is_requested[phase_idx] = self.variables[self.var_key][phase_idx] > 0

			next_phase = super().calculate_next_phase()
			if self.is_requested[phase_idx]:
				next_phase = self.get_transition(self.next_ped[phase_idx])
				self.is_requested[phase_idx] = False
		else:
			next_phase = super().calculate_next_phase()
		
		return next_phase