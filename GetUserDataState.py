from JarvisBaseState import JarvisBaseState
from ErmrestHandler import ErmrestHandler

class GetExperimentState(JarvisBaseState):
	
	def __init__(self,request,session):
		super(self.__class__,self).__init__()
		self._request = request
		self._session = session
		self._ermrest = ErmrestHandler("ec2-54-172-182-170.compute-1.amazonaws.com","root","root")

	def handle_input(self):
		experiment_id = self._get_experiment_id()
		current_experiment = self._get_experiment(experiment_id)
		#switch state: ValidateIntentState
	
	def _get_user_data(self):
		current_user = str(self._get_current_user(self._ermrest)[0]["user"])
		user_data = self._ermrest.get_data(1,"sample7",current_user)
		return user_data

	def _get_experiment(self,experiment_id):
		experiment_id = str(experiment_id)
		user_data = self._get_user_data()
		for experiment in user_data:
			if experiment["experiment_id"] == experiment_id:
				return experiment
		return {}
	
	def _get_experiment_id(self):
		if (self._slot_exists("EID",request)):
			return self._get_slot_value("EID",request)
		else:
			return None
