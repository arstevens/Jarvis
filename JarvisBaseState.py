import abc

class JarvisBaseState(object):

	__metaclass__ = abc.ABCMeta

	def __init__(self):
		self._request = "request variable goes here" 
		self._session = "session variable goes here"
		self._speech_output = "Jarvis speech output"
		self._card_title = "Alexa app card title"
		self._card_output = "Alexa app card output"
		self._reprompt_text = "Jarvis speech reprompt"
		self._should_end_session = False
	
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
	
	def _get_current_user(self,ermrest_handler):
		current_user = ermrest_handler.get_table_data(7,"current_user")
		return current_user
