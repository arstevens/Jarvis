#State_Imports===================================
from JarvisStates import *
#State_Handler===================================
class JarvisStateHandler(object):

	def __init__(self,request,session,ermrest):
		self._request = request
		self._session = session
		self._ermrest = ermrest
		self._return_value = None 
		try:
			#States all return the name of the next state, except for ReturnState.
			#ReturnState returns the alexa response to be built and said to the user.	
			self._states = {"AuthenticateState":AuthenticateState(self._request,self._session,self._ermrest),
				"GetIntentState":GetIntentState(self._request,self._session,self._ermrest),
				"ExperimentOpenCloseState":ExperimentOpenCloseState(self._request,self._session,self._ermrest),
				"LoginState":LoginState(self._request,self._session,self._ermrest),
				"LogoutState":LogoutState(self._request,self._session,self._ermrest),
				"ValidateState":ValidateState(self._request,self._session,self._ermrest),
				"IntentState":IntentState(self._request,self._session,self._ermrest),
				"ReturnState":ReturnState(self._request,self._session,self._ermrest)}
		except Exception as exc:
			print("[!] State Creation Error: "+str(exc))
		#Always starts with AuthenticateState
		self.current_state = self._states["AuthenticateState"]
	
	def run_states(self):
		#runs the state machine and handles state switching.
		while (True):
			new_state = self.current_state.handle_input()
			if (new_state not in self._states): #checks to see if what was returned could be the alexa response value
				self._return_value = new_state
				break
			else:
				self.current_state = self._states[new_state]
		return self._return_value
			
