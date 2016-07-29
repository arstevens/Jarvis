#===================================Imports===================================================
from JarvisBaseState import JarvisBaseState
from ErmrestHandler import ErmrestHandler
from GelElectrophoresis import GelElectrophoresis
from DataRetrieval import DataRetrieval
import re
#===================================Authenticate==============================================
class AuthenticateState(JarvisBaseState):
	
	def __init__(self,request,session,ermrest):
		#Checks if a user is logged in.
		#If not it switches to LoginState.
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest
		print("initiated authenticate")
		
	def handle_input(self):
		print("in authenticate")
		current_user = self._get_current_user()
		if (current_user):
			return "GetIntentState"	
		else:
			return "LoginState"	

#===================================GetIntentState==============================================
class GetIntentState(JarvisBaseState):
	
	def __init__(self,request,session,ermrest):
		#Gets the intent of the user then redirects the request to the proper state.
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest
		self._open_close_states = ['ExperimentOpenIntent','ExperimentCloseIntent']
		print("initiated getintent")

	
	def handle_input(self):
		print("In GetIntentState")
		intent_name = self._get_intent_name(self._request)

		if intent_name == "LogoutIntent":
			return "LogoutState"

		elif intent_name == "GetUserNameIntent":
			current_user = self._get_current_user()
			if (current_user):
				self._speech_output = "The current user is, {}".format(current_user)
				self._set_session_data("jarvis_response",self._speech_output)
			else:
				self._speech_output = "No user is logged in at the moment."
				self._set_session_data("jarvis_response",self._speech_output)

			return "ReturnState"

		elif intent_name == "LoginIntent":
			print("In login intent")
			self._speech_output = "A user is already logged in. Please log that user out before proceding"
			self._set_session_data("jarvis_response",self._speech_output)
			return "ReturnState"

		elif intent_name in self._open_close_states: 
			return "ExperimentOpenCloseState"

		else:
			return "ValidateState"
	
#===================================GetExperiment==============================================
class ExperimentOpenCloseState(JarvisBaseState):
	
	def __init__(self,request,session,ermrest):
		#Loads an experiment if the user wishes to.
		#Continues from the point the user left off if incomplete.
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest
		self._intent = self._get_intent_name(self._request)
		self._experiment_id = self._get_slot_value("EID",self._request)
		print('initiated get experiment')

	def handle_input(self):
		if self._intent == "ExperimentOpenIntent":
			return_value = self._experiment_open()
		else:
			return_value = self._experiment_close()

		return return_value
	
	def _experiment_open(self):
		#must load the last step the user completed into memory
		completed_step = self._get_last_step(self._experiment_id)
		success = self._set_completed_step(completed_step)
		if (success):
			return "IntentState"
		else:
			self._clear("step_completed")
			self._speech_output = "The experiment you wish to open does not exist." 
			self._set_session_data("jarvis_response",self._speech_output)
			return "ReturnState"
	
	def _experiment_close(self):
		self._clear("step_completed")
		self._set_session_data("current_experiment_id",None)
		self._speech_output = "Experiment closed. Please load an old experiment or start a new one."
		self._set_session_data("jarvis_response",self._speech_output)
		return "ReturnState"
	
#===================================Login==============================================
class LoginState(JarvisBaseState):
	
	def __init__(self,request,session,ermrest):
		#Checks if username was provided to log user in.
		#If so, logs user in and starts a session.
		#If not, asks user for their username.
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest
		print("initiated login")
	
	def handle_input(self):
		print("in login")
		username = self._get_slot_value("UserName",self._request).lower()
		if (username):
			self._speech_output = "Hello {}. Your session has begun".format(username)
			self._set_session_data("jarvis_response",self._speech_output)
			self._set_session_data("user",username)
			return "ReturnState"
		else:
			self._speech_output = "No user is logged in at the moment. Please provide your username and your session will begin."
			self._set_session_data("jarvis_response",self._speech_output)
			return "ReturnState"
	
#===================================Logout==============================================
class LogoutState(JarvisBaseState):

	def __init__(self,request,session,ermrest):
		#Logs user out and clears the current session info.
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest
		print("initiated logout")
	
	def handle_input(self):
		print("in logout state")
		self._clear("session_info")
		self._clear("step_completed")
		return "ReturnState"
		
#===================================Validate==============================================
class ValidateState(JarvisBaseState):
	
	def __init__(self,request,session,ermrest):
		#Checks if the intent of the user is allowed based on their previous input.
		#Prevents step jumping when running an experiment.
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest
		self._possible_intent_mappings = {
					'exp-selection': ["ExperimentGelSelectionIntent"],
					'gel-selection':["ExperimentGelMixtureStartIntent"],
					'mixture-start':["ExperimentGelMixtureEndIntent",
							"ExperimentGelMixtureDoneIntent"],
					'mixture-end':["ExperimentLoadingGelStartIntent"],
					'gel-loading-start':["ExperimentLoadingWellCountIntent"],
					'sample-count':["ExperimentLoadingSampleAssignmentIntent",
							"ExperimentLoadingSampleAssignmentMultiIntent",
							"ExperimentLoadingGelDoneIntent"],
					'gel-loading-end':["ExperimentPowerSupplyStartIntent"],
					'power-start':["ExperimentPowerSupplyEndIntent","ExperimentPowerSupplyCheckIntent"],
					'power-end':["ExperimentEndIntent"],
					'exp-end':["GetEIDIntent","GetStartDateIntent","GetEndDateIntent",
						"GetSampleCountIntent","GetWellSampleAssignmentIntent",
						"GetSampleWellAssignmentIntent"]}
		print("initiated validate")

	def handle_input(self):
		print("in validate state")
		last_step = self._get_completed_step()
		intent_name = self._get_intent_name(self._request)
		valid_intents = None
		
		if (last_step != None):
			#if a step is completed get the possible next steps
			valid_intents = self._possible_intent_mappings[last_step]

		elif (last_step == None):
			#if no steps have been completed
			if (intent_name == "ExperimentStartIntent"):
				return "IntentState"

			elif (intent_name == "ExperimentSelectionIntent"):
				id_number = int(self._get_slot_value("EID",self._request))
				print(id_number)
				#checks if the experiment id has already been taken
				if (self._is_id_taken(id_number)):
					print("in true!")
					self._speech_output = "The expeirment id you chose is already taken"
					self._set_session_data("jarvis_response",self._speech_output)
					return "ReturnState"
				return "IntentState"

		if (intent_name in valid_intents):
			return "IntentState"
			
		else:
			self._speech_output = "Your input was invalid." 
			self._set_session_data("jarvis_response",self._speech_output)
			return "ReturnState"

	
	def _get_completed_step(self):
		#gets the previous step the user completed
		try:
			last_step = self._ermrest.get_data(7,"step_completed")[0]
			last_step = last_step['completed_step']
		except:
			last_step = None
		
		return last_step

	def _is_id_taken(self,id_number):
		current_user = self._get_current_user()
		experiment_ids = []

		experiments = self._ermrest.get_data(7,"experiment_data","/user="+current_user)

		if (len(experiments) == 0):
			#user has no experiments yet
			return False
		
		for experiment in experiments:
			experiment_ids.append(int(experiment['experiment_id']))

		if id_number in experiment_ids:
			return True
		return False

#===================================Intent==============================================
class IntentState(JarvisBaseState):
	
	def __init__(self,request,session,ermrest):
		#runs the corresponding function for each experiment intent.
		#Sets the speech output for jarvis to say.
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest
		self._user = self._ermrest.get_data(7,"session_info")[0]["user"]
		self._intent = self._get_intent_name(request)
		self._experiment_id = self._get_experiment_id(self._request,self._ermrest)
		self._experiment_handler = GelElectrophoresis(self._user,self._experiment_id,self._ermrest) #contains methods for each experiment intent
		self._data_retriever = DataRetrieval(self._ermrest,self._experiment_id,self._user) #contains methods for get intents
		print("initiated intent")
	
	def handle_input(self):
		print("in IntentState")

		if (re.search("Experiment",self._intent)):
			#if the request is an experiment request, run these
			if self._intent == "ExperimentLoadingSampleAssignmentIntent":
				sample_type = self._get_slot_value("SampleType",self._request)
				well_number = self._get_slot_value("WellNumber",self._request)
				self._speech_output = self._experiment_handler.experiment_loading_sample_assignment_intent(sample_type,well_number)	
			elif self._intent == "ExperimentLoadingSampleAssignmentMultiIntent":
				sample_types = [self._get_slot_value("SampleType",self._request),self._get_slot_value("SampleTypeTwo",self._request)]
				well_numbers = [self._get_slot_value("WellNumber",self._request),self._get_slot_value("WellNumberTwo",self._request)]
				self._experiment_handler.experiment_loading_sample_assignment_intent(sample_types[0],well_numbers[0])
				self._speech_output = self._experiment_handler.experiment_loading_sample_assignment_intent(sample_types[1],well_numbers[1])
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
				self._speech_output = self._experiment_handler.experiment_gel_mixture_start_intent()
			elif self._intent == "ExperimentGelMixtureEndIntent":
				self._speech_output = self._experiment_handler.experiment_gel_mixture_end_intent()
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
			elif self._intent == "ExperimentOpenIntent":
				self._speech_output = "Experiment {} has been loaded".format(str(self._experiment_id))

		else:
			#if the request is a retrieve intent, run these
			if self._intent == "GetEIDIntent":
				self._speech_output = self._data_retriever.get_experiment_id_intent()
			elif self._intent == "GetStartDateIntent":
				self._speech_output = self._data_retriever.get_start_date_intent()
			elif self._intent == "GetEndDateIntent":
				self._speech_output = self._data_retriever.get_end_date_intent()
			elif self._intent == "GetSampleCountIntent":
				self._speech_output = self._data_retriever.get_sample_count_intent()
			elif self._intent == "GetWellSampleAssignmentIntent":
				well_number = self._get_slot_value("WellNumber",self._request)
				self._speech_output = self._data_retriever.get_well_sample_assignment_intent(well_number)
			elif self._intent == "GetSampleWellAssignmentIntent":
				sample = self._get_slot_value("SampleType",self._request).upper() #Must be upper case for correct pronounciation
				self._speech_output = self._data_retriever.get_sample_well_assignment_intent(sample)

		#Set the output response for ReturnState and set the completed step
		self._set_session_data("jarvis_response",self._speech_output)
		#Set the completed step (ExperimentStartIntent doesn't count as a step completed) 
		if self._intent != "ExperimentStartIntent":
			self._set_completed_step(self._get_last_step(self._experiment_id))

		return "ReturnState"
	
	def _get_experiment_id(self,request,ermrest):
		#gets the experiment ID from all possible sources. Returns None if no ID
		if (self._intent == "ExperimentStartIntent"):
			eid = None	

		elif (self._intent == "ExperimentSelectionIntent" or
			self._intent == "ExperimentOpenIntent"):
			eid = int(self._get_slot_value("EID",self._request))
			self._set_session_data("current_experiment_id",eid)

		else:
			eid = ermrest.get_data(7,"session_info")[0]['current_experiment_id']

		return eid
		
#===================================BuildResponse==============================================
class ReturnState(JarvisBaseState):

	def __init__(self,request,session,ermrest):	
		#All this state does is return the response value. 
		#Needed since other states must return the key for the next state.	
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ermrest

	def handle_input(self):
		response = self._ermrest.get_data(7,"session_info")[0]['jarvis_response']

		if (response == None):
			response = "Goodbye." #Logout clears all of the tables so this is the default.

		return response

