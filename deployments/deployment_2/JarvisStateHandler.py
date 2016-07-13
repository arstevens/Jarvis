#State_Imports===================================
from JarvisStates import *
#State_Handler===================================
class JarvisStateHandler(object):

	def __init__(self,request,session):
		self._request = request
		self._session = session
		self._return_value = None
		self._states = {"AuthenticateState":AuthenticateState(self._request,self._session),
				"GetIntentState":GetIntentState(self._request,self._session),
				"GetExperimentState":GetExperimentState(self._request,self._session),
				"LoginState":LoginState(self._request,self._session),
				"LogoutState":LogoutState(self._request,self._session),
				"GetUserDataState":GetUserDataState(self._request,self._session),
				"ValidateState":ValidateState(self._request,self._session),
				"IntentState":IntentState(self._request,self._session),
				"ReturnState":ReturnState(self._request,self._session)}
		self.current_state = self._states["AuthenticateState"]
	
	def handle_states(self):
		while (True):
			new_state = self.current_state.handle_input()
			if (new_state not in self._states): #checks to see if what was returned could be the alexa response value
				self._return_value = new_state
				break
			else:
				self.current_state = self._states[new_state]
		return self._return_value
			
