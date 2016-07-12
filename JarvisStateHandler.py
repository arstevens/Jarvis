#State_Imports===================================
from JarvisStates import *
#State_Handler===================================
class JarvisStateHandler(object):

	def __init__(self,request,session):
		self._request = request
		self._session = session
		self._should_end = False
		self._text_output = "Alexa says this"
		self._reprompt_text = "Sorry. I didn't get that"
		self._card_title = "Card title"
		self._card_output = "Card output"
		#states return [new state]
		self._states = {"AuthenticateState":AuthenticateState(self._request,self._session),
				"LoginState":LoginState(self._request,self._session),
				"GetUserDataState":GetUserDataState(self._request,self._session),
				"ValidateState":ValidateState(self._request,self._session)}
		self.current_state = self._states["AuthenticateState"]
	
	def handle_states(self):
		while (self._should_end == False):
			state_data = self.current_state.handle_input()
			self.current_state = self._states[state_data[0]]
			self._should_end = state_data[1]
