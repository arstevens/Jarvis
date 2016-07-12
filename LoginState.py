from JarvisBaseState import JarvisBaseState

class LoginState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
	
	def handle_input(self):
		username = self._get_username("UserName")
		if (username):
			#switch state: AuthenticateState
			pass
		else:
			#switch state: BuildResponseState
			pass
	
	def _get_username(self,slot_name):
		if (self._slot_exists(slot_name,self._request)):
			return self._get_slot_value(slot_name,self._request)
		else:
			return None
