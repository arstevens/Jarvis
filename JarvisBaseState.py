import abc
import logging
from ErmrestHandler import ErmrestHandler

class JarvisBaseState(object):

	__metaclass__ = abc.ABCMeta

	def __init__(self):
		self._request = "request variable goes here" 
		self._session = "session variable goes here"
		self._speech_output = "Jarvis speech output"
		self._card_title = "Alexa app card title"
		self._card_output = "Alexa app card output"
		self._steps = ['exp-start','exp-selection','get-selection','mixture-start','mixture-end',
		'gel-loading-start','sample-count','gel-loading-end','power-start','power-end','exp-end']
		self.logger = logging.getLogger()
		self._reprompt_text = "Jarvis speech reprompt"
		self._should_end_session = False
		self._ermrest = ErmrestHandler("ec2-54-172-182-170.compute-1.amazonaws.com","root","root")
	
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

	@staticmethod
	def _get_session_attribute(session):
		if 'attributes' in session:
			return session['attributes']
		else:
			return dict()

	def _get_slot_value(self, slot_name, intent_request):
		value = None
		try:
			if self._slot_exists(slot_name, intent_request):
				intent = self._get_intent(intent_request)
				value = intent['slots'][slot_name]['value']
			else:
				value = None
        	except Exception as exc:
            		self.logger.error("Error getting slot value for slot_name={0}".format(slot_name))

        	return value
	
	def _get_current_user(self):
		current_user = self._ermrest.get_data(7,"session_info","")[0]
		return current_user['user']
	
	def _set_session_data(self,column,new_data):
		user = self._get_current_user()
		extra_data = "/user="+user
		current_data = self._ermrest.get_data(7,"session_info",extra_data)[0]
		current_data[column] = new_data
		try:
			self._ermrest.delete_data(7,"session_info",extra_data)
			self._ermrest.put_data(7,"session_info",current_data)
			return True
		except Exception as exc:
			self.logger.error(str(exc))
			return False

	def _set_completed_step(self,new_step):
		data = self._ermrest.get_data(7,"step_completed","")[0]
		data['completed_step'] = new_step
		try:
			self._ermrest.delete_data(7,"step_completed","")
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
			self.logger.error(str(exc))
			return False
