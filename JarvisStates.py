#===================================Imports===================================================
from JarvisBaseState import JarvisBaseState
from ErmrestHandler import ErmrestHandler
#===================================Authenticate==============================================
class AuthenticateState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		
	def handle_input(self):
		current_user = self._get_current_user()
		if (current_user):
			return "GetIntentState"	
		else:
			return "LoginState"	
#===================================GetIntentState==============================================
class GetIntentState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
	
	def handle_input(self):
		intent_name = self._get_intent_name(request)

		if intent_name == "LogoutIntent":
			return "LogoutState"
		elif intent_name == "ExperimentStartIntent":
			return "NewExperimentIntent"
		elif intent_name == "OpenExperimentIntent":
			return "OpenExperimentState"
		else:
			return "ValidateState"
	
	def _upload_intent(self,intent_name):
		status = self._set_session_data("current_intent",intent_name)
		if (status):
			self.logger.info("[*] Upload succeded")
		else:
			self.logger.error("[!] Upload Failed: Check functions")


#===================================GetExperiment==============================================
class GetExperimentState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session

	def handle_input(self):
		completed_step = self._get_last_step()
		success = self._set_completed_step(completed_step)
		if (success):
			return "IntentState"
		else:
			self._clear("step_completed")
			self._speech_output = "Something went wrong. Check the logs" 
			self._set_session_data("jarvis_response",self._speech_output)
			return "BuildResponseState"
	
	def _get_last_step(self):
		experiment_id = self._get_experiment_id(self._request)
		experiment = self._get_experiment(experiment_id)
		steps_completed = experiment['states_completed'].split(",")
		last_step = steps_completed[len(steps_completed)-1]
		return last_step

	def _get_experiment(self,experiment_id):
		experiment_id = str(experiment_id)
		user = self._get_current_user()
		query = "/user="+user+"/experiment_id="+experiment_id
		try:
			experiment = self._ermrest.get_data(7,"experiment_data",query)
			return experiment	
		except Exception as exc:
			self.logger.error(str(exc))
			return {} 
	
#===================================Login==============================================
class LoginState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
	
	def handle_input(self):
		username = self._get_username("UserName")
		if (username):
			self._speech_output = "Hello {}. Your session has begun".format(username)
			self._set_session_data("jarvis_response",self._speech_output)
			return "BuildResponseState"	
		else:
			self._speech_output = "No user is logged in at the moment. 
					Please provide your username and 
					your session will begin."
			self._set_session_data("jarvis_response",self._speech_output)
			return "BuildResponseState"
	
	def _get_username(self,slot_name):
		if (self._slot_exists(slot_name,self._request)):
			return self._get_slot_value(slot_name,self._request)
		else:
			return None

#===================================Validate==============================================
class ValidateState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		#maps last step completed to what you can do next to prevent step jumping
		self._possible_intent_mappings = {'exp-start': ["ExperimentSelectionIntent"],
					'exp-selection': ["ExperimentGelSelectionIntent"],
					'gel-selection':["ExperimentGelMixtureStartIntent"],
					'mixture-start':["ExperimentGelMixtureEndIntent"],
					'mixture-end':["ExperimentLoadingGelStartIntent","ExperimentGelMixtureDoneIntent"],
					'gel-loading-start':["ExperimentLoadingWellCountIntent"],
					'sample-count':["ExperimentLoadingSampleAssignmentIntent"],
					'gel-loading-end':["ExperimentPowerSupplyStartIntent","ExperimentLoadingGelDoneIntent"],
					'power-start':["ExperimentPowerSupplyEndIntent","ExperimentPowerSupplyCheckIntent"],
					'power-end':["ExperimentEndIntent"],
					'exp-end':[""]}

	def handle_input(self):
		last_step = self._get_completed_step()
		intent_name = self._get_intent_name(request)
		if (last_step == None and intent_name == "ExperimentStartIntent"):
			return "IntentState"
		next_step = self._get_next_step(last_step)
		valid_intents = self._possible_intent_mappings[last_step]
		if intent_name in valid_intents:
			if intent_name != "ExperimentGelMixtureDoneIntent" and 
				intent_name != "ExperimentPowerSupplyCheckIntent":
				self._set_completed_step(self._steps[next_step]
			return "IntentState"
		else:
			self._speech_ouput = "Your input was invalid. If not, check the logs"
			self._set_session_data("jarvis_response",self._speech_output)
			return "BuildResponseState"

	
	def _get_completed_step(self):
		last_step = None
		try:
			last_step = self._ermrest.get_data(7,"step_completed","")[0]['completed_step']
		return last_step
	
	def _get_next_step(self,last_step):
		for step in range(len(self._steps)-1):
			if step == last_step:
				return step
		return False 

#===================================IntentState==============================================
class IntentState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._user = self._ermrest.get_data(7,"session_info","")[0]["user"]
		self._intent = self._get_intent_name(request)
		self._experiment_id = self._get_experiment_id(self._request)
		self._experiment_handler = GelElectrophoresis(self._user,self._experiment_id,self._ermrest)
	
	def handle_input(self):
		if self._intent == "ExperimentStartIntent":
			self._experiment_handler.experiment_start_intent()
		elif self._intent == "ExperimentSelectionIntent":
			self._experiment_handler.experiment_selection_intent("experiment_name")
		elif self._intent == "ExperimentGelSelectionIntent":
			self._experiment_handler.experiment_gel_selection_intent("gel_type")
		elif self._intent == "ExperimentGelMixtureStartIntent":
			self._experiment_handler.experiment_gel_mixture_start_intent()
		elif self._intent == "ExperimentGelMixtureEndIntent":
			self._experiment_handler.experiment_gel_mixture_end_intent()
		elif self._intent == "ExperimentGelMixtureDoneIntent":
			self._experiment_handler.experiment_gel_mixture_done_intent()
		elif self._intent == "ExperimentLoadingGelStartIntent":
			self._experiment_handler.experiment_loading_gel_start_intent()
		elif self._intent == "ExperimentLoadingWellCountIntent":
			self._experiment_handler.experiment_loading_well_count_intent("count")
		elif self._intent == "ExperimentLoadingSampleAssignmentIntent":
			self._experiment_handler.experiment_loading_sample_assignment_intent("sampletype",
												"#")
		elif self._intent == "ExperimentLoadingGelDoneIntent":
			self._experiment_handler.experiment_gel_loading_done_intent()
		elif self._intent == "ExperimentPowerSupplyStartIntent":
			self._experiment_handler.experiment_power_supply_start_intent()
		elif self._intent == "ExperimentPowerSupplyCheckIntent":
			self._experiment_handler.experiment_power_supply_check_intent()
	
