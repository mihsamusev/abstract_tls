from tlsagents.base import TLSAgent, TLSFactory
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
		queue = states["A"] + states["B"]
		objective = 0
		for elem in queue:
			objective += elem * elem
		return objective

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


@TLSFactory.register('stratego')
class StrategoTLS(TLSAgent):
	"""
	Controller class for a pedestrian responsive crosswalk controller
	"""
	def __init__(self, tls_id, constants=None, variables=None, data_query=None, optimizer=None):
		super().__init__(tls_id, constants, variables, data_query, optimizer)

		self.mpc_step = self.constants.get('mpc_step', 5)
		self.min_green = self.constants.get('min_green', 4)
		self.uppaal_model_template = self.constants.get('model_template')
		self.uppaal_query = self.constants.get('query', None)
		self.uppaal_verifyta = self.constants.get('verifyta', 'verifyta')
		self.uppaal_debug = self.constants.get('debug', False)

		self.optimizer = StategoOptimizer(
            templatefile=self.uppaal_model_template,
            model_cfg_dict=self.variables)

	def calculate_next_phase(self):
		next_phase = self.phase

		# read state
		self.variables = self.data_pipeline.extract()

		self.optimizer.init_simfile()
		self.optimizer.update_state(self.variables)
		self.optimizer.insert_state()

		durations, phase_seq  = self.optimizer.run(
			queryfile=self.uppaal_query,
			verifyta_path=self.uppaal_verifyta)