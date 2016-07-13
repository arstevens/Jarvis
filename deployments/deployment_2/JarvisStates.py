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
		
		elif intent_name == "ExperimentOpenIntent":
			return "GetExperimentState"
		
		else:
			return "ValidateState"
	
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
			return "ReturnState"
	
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
			return "ReturnState"
		else:
			self._speech_output = """No user is logged in at the moment. 
					Please provide your username and 
					your session will begin."""
			self._set_session_data("jarvis_response",self._speech_output)
			return "ReturnState"
	
	def _get_username(self,slot_name):
		if (self._slot_exists(slot_name,self._request)):
			return self._get_slot_value(slot_name,self._request)
		else:
			return None

#===================================Logout==============================================
class LogoutState(JarvisBaseState):

	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
	
	def handle_input(self):
		self._clear("session_info")
		self._clear("step_completed")
		return "ReturnState"
		
#===================================Validate==============================================
class ValidateState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		#maps last step completed to what you can do next in order prevent step jumping
		self._possible_intent_mappings = {'exp-start': ["ExperimentSelectionIntent"],
					'exp-selection': ["ExperimentGelSelectionIntent"],
					'gel-selection':["ExperimentGelMixtureStartIntent"],
					'mixture-start':["ExperimentGelMixtureEndIntent","ExperimentGelMixtureDoneIntent"],
					'mixture-end':["ExperimentLoadingGelStartIntent"],
					'gel-loading-start':["ExperimentLoadingWellCountIntent"],
					'sample-count':["ExperimentLoadingSampleAssignmentIntent","ExperimentLoadingGelDoneIntent"],
					'gel-loading-end':["ExperimentPowerSupplyStartIntent"],
					'power-start':["ExperimentPowerSupplyEndIntent","ExperimentPowerSupplyCheckIntent"],
					'power-end':["ExperimentEndIntent"],
					'exp-end':[""]}

	def handle_input(self):
		last_step = self._get_completed_step()
		intent_name = self._get_intent_name(request)
		try:
			valid_intents = self._possible_intent_mappings[last_step]
		except:
			valid_intents = None
		
		if (last_step == None and intent_name == "ExperimentStartIntent"):
			return "IntentState"
		
		if intent_name in valid_intents:
			return "IntentState"

		else:
			self._speech_ouput = "Your input was invalid. If not, check the logs"
			self._set_session_data("jarvis_response",self._speech_output)
			return "ReturnState"

	
	def _get_completed_step(self):
		last_step = None
		try:
			last_step = self._ermrest.get_data(7,"step_completed")[0]['completed_step']
		except Exception as exc:
			self.logger.error(str(exc))
		return last_step
	
#===================================Intent==============================================
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
		if self._intent == "ExperimentLoadingSampleAssignmentIntent":
			sample_type = self._get_slot_value("SampleType",self._request)
			well_number = self._get_slot_value("WellNumber",self._request)
			self._speech_output = self._experiment_handler.experiment_loading_sample_assignment_intent(sample_type,well_number)	

		elif self._intent == "ExperimentSelectionIntent":
			experiment_name = self._get_slot_value("ExperimentName",self._request)
			self._speech_output = self._experiment_handler.experiment_selection_intent(experiment_name)

		elif self._intent == "ExperimentGelSelectionIntent":
			gel_type = self._get_slot_value("GelName",self._request)
			self._speech_output = self._experiment_handler.experiment_gel_selection_intent(gel_type)
	
		elif self._intent == "ExperimentLoadingWellCountIntent":
			well_count = self._get_slot_value("WellCount",self._request)
			self._speech_output = self._experiment_handler.experiment_loading_well_count_intent(well_count)
		
		elif self._intent == "ExperimentStartIntent":
			self._speech_output = self._experiment_handler.experiment_start_intent()
		elif self._intent == "ExperimentGelMixtureStartIntent":
			self_speech_output = self._experiment_handler.experiment_gel_mixture_start_intent()
		elif self._intent == "ExperimentGelMixtureEndIntent":
			self._speech_output = self._experiment_handler.experiment_gel_mixture_end_intent()
		elif self._intent == "ExperimentGelMixtureDoneIntent":
			self._speech_output = self._experiment_handler.experiment_gel_mixture_done_intent()
		elif self._intent == "ExperimentLoadingGelStartIntent":
			self._speech_output = self._experiment_handler.experiment_loading_gel_start_intent()
		elif self._intent == "ExperimentLoadingGelDoneIntent":
			self._speech_output = self._experiment_handler.experiment_gel_loading_done_intent()
		elif self._intent == "ExperimentPowerSupplyStartIntent":
			self._speech_output = self._experiment_handler.experiment_power_supply_start_intent()
		elif self._intent == "ExperimentPowerSupplyCheckIntent":
			self._speech_output = self._experiment_handler.experiment_power_supply_check_intent()
		elif self._intent == "ExperimentPowerSupplyEndIntent":
			self._speech_output = self._experiment_handler.experiment_power_supply_end_intent()
		elif self._intent == "ExperimentEndIntent":
			self._speech_output = self._experiment_handler.experiment_end_intent()

		self._set_session_data("jarvis_response",self._speech_output)
		self._set_completed_step(self._get_last_step())
	
		return "ReturnState"
	
#===================================BuildResponse==============================================
class ReturnState(JarvisBaseState):

	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		try:
			self._speech_output = self._ermrest.get_data(7,"session_info","")[0]["jarvis_response"]
		except:
			self._speech_output = "Goodbye."

	def handle_input(self):
		#All this class does is return the response value. 
		#Not needed just makes the state machine make more sense.	
		return self._speech_output

