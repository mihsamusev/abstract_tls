from tlsagents.base import TLSAgent, TLSFactory


@TLSFactory.register('stratego')
class StrategoTLS(TLSAgent):
	"""
	Controller class for a pedestrian responsive crosswalk controller
	"""
	def __init__(self, tls_id, constants=None, variables=None, data_query=None, optimizer=None):
		super().__init__(tls_id, constants, variables, data_query, optimizer)

		self.mpc_step = self.constants.get('mpc_step', 5)
		self.min_green = self.constants.get('min_green', 4)
		self.uppaal_query = self.constants.get('query', None)
		self.uppaal_verifyta = self.constants.get('verifyta', 'verifyta')
		self.uppaal_debug = self.constants.get('debug', False)

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