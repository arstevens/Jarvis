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
		experiment_id = self._get_experiment_id()
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
	
	def _get_experiment_id(self):
		if (self._slot_exists("EID",self._request)):
			return self._get_slot_value("EID",self._request)
		else:
			return None

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
		next_step = self._get_next_step(last_step)
		intent_name = self._get_intent_name(request)
		valid_intents = self._possible_intent_mappings[last_step]
		if intent_name in valid_intents:
			self._set_completed_step(self._steps[next_step]
			return "IntentState"
		else:
			self._speech_ouput = "Your input was invalid. If not, check the logs"
			self._set_session_data("jarvis_response",self._speech_output)
			return "BuildResponseState"

	
	def _get_completed_step(self):
		last_step = self._ermrest.get_data(7,"step_completed","")[0]['completed_step']
		return last_step
	
	def _get_next_step(self,last_step):
		for step in range(len(self._steps)-1):
			if step == last_step:
				return step
		return False 
