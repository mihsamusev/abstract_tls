from tlsagents.base import TLSAgent, TimedTLS, TLSFactory
import strategoutil as sutil
from strategoutil import StrategoController


class StategoOptimizer(StrategoController):
	def __init__(self, templatefile, model_cfg_dict):
		super().__init__(templatefile, model_cfg_dict, interactive_bash=False)
		 # tag left in model_template.xml
		self.tagRule = "//TAG_{}"
		self.objective = 0

	def format_state(self, value):
		"""
		Lists and scalars are formatted accordingly
		"""
		if isinstance(value, list):
			value = sutil.array_to_stratego(value)
		else:
			value = str(value)
		return value

	def update_objective(self):
		self.objective += self.get_objective(self.states)

	def get_objective(self, states):
		"""
		queue = states["A"] + states["B"]
		objective = 0
		for elem in queue:
			objective += elem * elem
		"""
		return 0

	def update_state(self, new_values):
		super().update_state(new_values)
		self.update_objective()

	def insert_state(self):
		"""
		Override insert state method to format arrays and scalars accodingly
		"""
		for name, value in self.states.items():
				tag = self.tagRule.format(name)
				value = self.format_state(value)
				sutil.insert_to_modelfile(self.simulationfile, tag, value)

	def run(self, queryfile="", learning_args=None, verifyta_command="verifyta"):
		output = super().run(queryfile, learning_args, verifyta_command)
		tpls = sutil.get_int_tuples(output)
		result = sutil.get_duration_action(tpls, max_time=1000)
		durations, actions = list(zip(*result)) 
		return durations, actions


@TLSFactory.register_agent('stratego')
class StrategoTLS(TimedTLS):
	"""
	Controller class for a pedestrian responsive crosswalk controller
	"""
	def __init__(self, tls_id, constants=None, variables=None,
		data_query=None, optimizer=None):
		super().__init__(tls_id, constants, variables, data_query, optimizer)

		self.mpc_step = self.constants.get('mpc_step', 5)
		self.min_green = self.constants.get('min_green', 4)
		self.uppaal_model_template = self.constants.get('model_template')
		self.uppaal_query = self.constants.get('verifyta_query', "")
		self.uppaal_verifyta = self.constants.get('verifyta_command', 'verifyta')
		self.uppaal_debug = self.constants.get('debug', False)
		
		self.n_movement_phases = self.constants.get('n_movement_phases') 
		self.movement_phase = True 
		
		self.transitions = self.get_transitions()
		self.optimizer = StategoOptimizer(
            templatefile=self.uppaal_model_template,
            model_cfg_dict=self.variables)

	
	def get_transitions(self):
		"""
		Calculate transitions from
		"""
		transitions = []
		for p in self.phase_list[self.n_movement_phases:]:
			i, j = map(int, p.name.strip("( )").split(","))
			transitions.append((i, j))
		return transitions
	
	def calculate_next_phase(self):
		self.variables = self.data_pipeline.extract()

		self.movement_phase = self.phase < self.n_movement_phases

		# on k-th step of each movement phase
		if self.movement_phase and self.elapsed >= self.min_green and self.elapsed % self.mpc_step == 0:
			self.optimizer.init_simfile()
			self.optimizer.update_state(self.variables)
			
			# fix the phase from int to boolean array
			is_active = [
				1 if self.phase == i else 0 for i in range(self.n_movement_phases)]
			self.optimizer.update_state({"is_active": is_active})
			self.optimizer.insert_state()

			durations, phase_seq  = self.optimizer.run(
			queryfile=self.uppaal_query,
			verifyta_command=self.uppaal_verifyta)
			
			# decide next movement phase
			next_movement_phase = phase_seq[0]
			next_duration = durations[0]

			if next_duration == self.min_green and len(phase_seq) > 1:
				next_movement_phase = phase_seq[1]
				next_duration = durations[1]
			
			# decide if transition is required
			next_phase = next_movement_phase
			if self.phase != next_phase:
				transition_phase = self.transitions.index((self.phase, next_phase))
				next_phase = self.n_movement_phases + transition_phase

		else:
			next_phase = super().calculate_next_phase()
		
		return next_phase


@TLSFactory.register_agent('stratego2')
class StrategoTLS(TimedTLS):
	"""
	Controller class for a pedestrian responsive crosswalk controller
	"""
	def __init__(self, tls_id, constants=None, variables=None,
		data_query=None, optimizer=None):
		super().__init__(tls_id, constants, variables, data_query, optimizer)

		self.mpc_step = self.constants.get('mpc_step', 5)
		self.min_green = self.constants.get('min_green', 4)
		self.uppaal_model_template = self.constants.get('model_template')
		self.uppaal_query = self.constants.get('verifyta_query', "")
		self.uppaal_verifyta = self.constants.get('verifyta_command', 'verifyta')
		self.uppaal_debug = self.constants.get('debug', False)
		
		self.n_movement_phases = self.constants.get('n_movement_phases') 
		self.movement_phase = True 
		
		self.transitions = self.get_transitions()
		self.optimizer = StategoOptimizer(
            templatefile=self.uppaal_model_template,
            model_cfg_dict=self.variables)

	
	def get_transitions(self):
		"""
		Calculate transitions from
		"""
		transitions = []
		for p in self.phase_list[self.n_movement_phases:]:
			i, j = map(int, p.name.strip("( )").split(","))
			transitions.append((i, j))
		return transitions
	
	def calculate_next_phase(self):
		self.variables = self.data_pipeline.extract()

		self.movement_phase = self.phase < self.n_movement_phases

		# on k-th step of each movement phase
		if self.movement_phase and self.elapsed >= self.min_green and self.elapsed % self.mpc_step == 0:
			self.optimizer.init_simfile()
			self.optimizer.update_state(self.variables)
			self.optimizer.insert_state()

			_, phase_seq  = self.optimizer.run(
			queryfile=self.uppaal_query,
			verifyta_command=self.uppaal_verifyta)
			
			# ecide next movement phase and if transition is required
			next_phase = phase_seq[0]
			if self.phase != next_phase:
				transition_phase = self.transitions.index((self.phase, next_phase))
				next_phase = self.n_movement_phases + transition_phase

		else:
			next_phase = super().calculate_next_phase()
		
		return next_phase