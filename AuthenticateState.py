from JarvisBaseState import JarvisBaseState
from ErmrestHandler import ErmrestHandler

class AuthenticateState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ErmrestHandler("ec2-54-172-182-170.compute-1.amazonaws.com",
						"root","root")

	def handle_input(self):
		current_user = self._get_current_user(self._ermrest)
		if (current_user):
			pass	
			#switch state: GrabCompletedStepsState 
		else:
			pass
			#switch state: LoginState

