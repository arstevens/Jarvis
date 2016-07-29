from AlexaBaseHandler import AlexaBaseHandler
from GelElectrophoresis import GelElectrophoresis
from JarvisStateHandler import JarvisStateHandler
from ErmrestHandler import ErmrestHandler
import logging


class AlexaJarvisHandler(AlexaBaseHandler):

	#The Concrete implementation of the AlexaBaseHandler. 
	def __init__(self):
		super(self.__class__, self).__init__()
		self._card_title = "Jarvis Response"
		self._card_output = "Jarvis card output"
		self._reprompt_text = "Sorry. I didn't get that"
		self._ermrest = ErmrestHandler("ec2-54-172-182-170.compute-1.amazonaws.com",'root','root')

	def on_processing_error(self, event, context, exc):
		self.logger.error("on_processing_error")
		self._speech_output = "Sorry. I didn't understand what you said"
		return self._build_response(dict())

	def on_launch(self, request, session):
		self._speech_output = "Hello, I am Jarvis your personal assistant and lab partner."
		current_user = self._ermrest.get_data(7,"session_info")[0]['user']
		if (current_user != None):
			self._speech_output = "Hello {}, how may i help you".format(current_user)

		self.logger.info("on_launch")
		session_attributes = self._get_session_attribute(session)
		return self._build_response(session_attributes)

	def on_session_started(self, request, session):
		self.logger.info("on_session_started")
		return self.on_launch(request, session)

	def on_intent(self, request, session):
		#runs state machine to handle intents and store data
		#in the ermrest relational database.
		self.logger.info("on_intent")
		session_attributes = self._get_session_attribute(session)
		jarvis_state_handler = JarvisStateHandler(request,session,self._ermrest)
		self._speech_output = jarvis_state_handler.run_states()
		return self._build_response(session_attributes) 

	def on_session_ended(self, request, session):
		session_attributes = self._get_session_attribute(session)
		self._speech_output = "Session is ending."
		return self._build_response(session_attributes)

