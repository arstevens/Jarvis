import abc
import logging
from ErmrestHandler import ErmrestHandler

class JarvisBaseState(object):

	__metaclass__ = abc.ABCMeta

	def __init__(self):
		self._request = "request variable goes here" 
		self._session = "session variable goes here"
		self._speech_output = "Jarvis speech output"
		self._reprompt_text = "Sorry. I didn't get that"
		self._ermrest = "Ermrest Handler goes here" 
	
	@abc.abstractmethod
	def handle_input(self):
		"""The handle_input method is the front end for your State.
		It will be the method that is called by the main handler. All
		other methods described in the child class should not be run solo 
		and should only be called through this method or by other methods 
		called by this method."""
		return

##=============================Helper Methods=============================================

	def _get_intent(self, intent_request):
		if 'intent' in intent_request:
			return intent_request['intent']
        	else:
            		return None

	def _get_intent_name(self, intent_request):
		intent = self._get_intent(intent_request)
		intent_name = None
		if intent is not None and 'name' in intent:
			intent_name = intent['name']

		return intent_name

	def _slot_exists(self, slot_name, intent_request):
		intent = self._get_intent(intent_request)
		if intent is not None:
			return slot_name in intent['slots']
		else:
			return False

	def _get_slot_value(self, slot_name, intent_request):
		value = None
		try:
			if self._slot_exists(slot_name, intent_request):
				intent = self._get_intent(intent_request)
				value = intent['slots'][slot_name]['value']
			else:
				value = None
        	except Exception as exc:
            		print("Error getting slot value for slot_name={0}".format(slot_name))

        	return value
	
	def _get_current_user(self):
		current_user = self._ermrest.get_data(7,"session_info","")[0]
		return current_user['user']
	
	def _set_session_data(self,column,new_data):
		current_data = self._ermrest.get_data(7,"session_info")[0]
		current_data[column] = new_data
		try:
			self._ermrest.delete_data(7,"session_info")
			self._ermrest.put_data(7,"session_info",current_data)
			return True
		except Exception as exc:
			print(str(exc))
			return False

	def _set_completed_step(self,new_step):
		data = self._ermrest.get_data(7,"step_completed")[0]
		data['completed_step'] = new_step
		try:
			self._ermrest.delete_data(7,"step_completed")
			self._ermrest.put_data(7,"step_completed",data)
			return True
		except:
			return False

	def _get_experiment_id(self,request):
		if (self._slot_exists("EID",request)):
			return self._get_slot_value("EID",request)
		else:
			return None
		
	def _clear(self,table_name):
		clean_data = self._ermrest.get_data(7,table_name,"")[0]
		for key in clean_data:
			clean_data[key] = None

		try:
			self._ermrest.delete_data(7,table_name)
			self._ermrest.put_data(7,table_name,clean_data)
			return True
		except Exception as exc:
			print(str(exc))
			return False

	def _get_last_step(self):
		experiment_id = self._get_experiment_id(self._request)
		experiment = self._get_experiment(experiment_id)
		steps_completed = experiment['states_completed'].split(",")
		last_step = steps_completed[len(steps_completed)-1]
		print("returning last step")
		return last_step

	def _get_experiment(self,experiment_id):
		experiment_id = str(experiment_id)
		user = self._get_current_user()
		query = "/user="+user+"/experiment_id="+experiment_id
		try:
			experiment = self._ermrest.get_data(7,"experiment_data",query)
			return experiment	
		except Exception as exc:
			print(str(exc))
			return {} 
	
