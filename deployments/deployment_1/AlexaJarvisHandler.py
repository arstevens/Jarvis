from AlexaBaseHandler import AlexaBaseHandler
from GelElectrophoresis import GelElectrophoresis
from JarvisStateHandler import JarvisStateHandler
from ErmrestHandler import ErmrestHandler
import logging


class AlexaJarvisHandler(AlexaBaseHandler):

    def __init__(self):
        super(self.__class__, self).__init__()
        self._card_title = "Jarvis Response"
        self._card_output = "Jarvis card output"

    def _test_response(self, msg, request, session):
        session_attributes = self._get_session_attribute(session)
        self._speech_output = "".format(msg)
        return self._build_response(session_attributes)

    def on_processing_error(self, event, context, exc):
        self.logger.error(str(event)+str(context)+str(exc))
        self._speech_output = "Jarvis experienced problems. Please check logs"
        return self._build_response(dict())

    def on_launch(self, request, session):
        self.logger.info(str(request)+str(session))
        session_attributes = self._get_session_attribute(session)
        self._speech_output = "Hello, I am Jarvis your lab partner."
        return self._build_response(session_attributes)

    def on_session_started(self, request, session):
        self.logger.info(str(request)+str(session))
        return self.on_launch(request, session)

    def on_intent(self, request, session):
        self.logger.info(str(request)+str(session))
	jarvis_state_handler = JarvisStateHandler(request,session)
	response = jarvis_state_handler.handle_state()
	return response

    def on_session_ended(self, request, session):
        session_attributes = self._get_session_attribute(session)
        self._speech_output = "Session is ending."
        return self._build_response(session_attributes)

