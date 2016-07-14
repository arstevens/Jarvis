from AlexaBaseHandler import AlexaBaseHandler
from GelElectrophoresis import GelElectrophoresis
from JarvisStateHandler import JarvisStateHandler
from ErmrestHandler import ErmrestHandler
import logging


class AlexaJarvisHandler(AlexaBaseHandler):

	#The Concrete implementation of the AlexaBaseHandler. 
	#Also implements the JarvisStateHandler for intents.
	def __init__(self):
		super(self.__class__, self).__init__()
		self._card_title = "Jarvis Response"
		self._card_output = "Jarvis card output"
		self._reprompt_text = "Sorry. I didn't get that"
		self._ermrest = ErmrestHandler("ec2-54-172-182-170.compute-1.amazonaws.com",'root','root')

	def on_processing_error(self, event, context, exc):
		self.logger.error("on_processing_error")
		try:
			self._ermrest.delete_data(7,"session_info")
			self._ermrest.put_data(7,"session_info",{"user":None,"jarvis_response":None})
		except:
			pass
		self._speech_output = "Jarvis experienced problems. Please check logs"
		return self._build_response(dict())

	def on_launch(self, request, session):
		self.logger.info("on_launch")
		session_attributes = self._get_session_attribute(session)
		self._speech_output = "Hello, I am Jarvis your lab partner."
		return self._build_response(session_attributes)

	def on_session_started(self, request, session):
		self.logger.info("on_session_started")
		return self.on_launch(request, session)

	def on_intent(self, request, session):
		self.logger.info("on_intent")
		session_attributes = self._get_session_attribute(session)
		print("made attribute")
		jarvis_state_handler = JarvisStateHandler(request,session,self._ermrest)
		print("Made state handler")
		self._speech_output = jarvis_state_handler.handle_states()
		print("created speech output:"+self._speech_output)
		return self._build_response(session_attributes) 

	def on_session_ended(self, request, session):
		print("ending")
		session_attributes = self._get_session_attribute(session)
		self._speech_output = "Session is ending."
		return self._build_response(session_attributes)

