import abc
import logging


class AlexaBaseHandler(object):
    """
    Base class for a python Alexa Skill Set.  Concrete implementations
    are expected to implement the abstract methods.

    See the following for Alexa details:
    https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/handling-requests-sent-by-alexa
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self._card_title = "test Response"
        self._card_output = "test card output"
        self._speech_output = ''
        # If the user either does not reply to the welcome message or says something
        # that is not understood, they will be prompted again with this text.
        self._reprompt_text = ''
        self._should_end_session = True
        self._speech_output = ''

    @abc.abstractmethod
    def on_launch(self, launch_request, session):
        """
        Implement the LaunchRequest.  Called when the user issues a:
        Alexa, open <invocation name>
        :param launch_request:
        :param session:
        :return: the output of _build_response
        """
        pass

    @abc.abstractmethod
    def on_session_started(self, session_started_request, session):
        pass

    @abc.abstractmethod
    def on_intent(self, intent_request, session):
        """
        Implement the IntentRequest
        :param intent_request:
        :param session:
        :return: the output of _build_response
        """
        pass

    @abc.abstractmethod
    def on_session_ended(self, session_end_request, session):
        """
        Implement the SessionEndRequest
        :param session_end_request:
        :param session:
        :return: the output of _build_response
        """
        pass

    @abc.abstractmethod
    def on_processing_error(self, event, context, exc):
        """
        If an unexpected error occurs during the process_request method
        this handler will be invoked to give the concrete handler
        an opportunity to respond gracefully

        :param exc exception instance
        :return: the output of _build_response
        """
        pass

    def process_request(self, event, context):
        """
        Helper method to process the input Alexa request and
        dispatch to the appropriate on_ handler
        :param event:
        :param context:
        :return: response from the on_ handler
        """
        # if its a new session, run the new session code
        try:
            response = None
            if event['session']['new']:
                self.on_session_started({'requestId': event['request']['requestId']}, event['session'])

                # regardless of whether its new, handle the request type
            if event['request']['type'] == "LaunchRequest":
                response = self.on_launch(event['request'], event['session'])
            elif event['request']['type'] == "IntentRequest":
                response = self.on_intent(event['request'], event['session'])
            elif event['request']['type'] == "SessionEndedRequest":
                response = self.on_session_ended(event['request'], event['session'])

        except Exception as exc:
            response = self.on_processing_error(event, context, exc)

        return response

    # --------------- Helpers that build all of the responses ----------------------
    def _build_speechlet_response(self):
        """
        Internal helper method to build the speechlet portion of the response
        :param card_title:
        :param card_output:
        :param speech_output:
        :param reprompt_text:
        :param should_end_session:
        :return:
        """
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': self._speech_output
            },
            'card': {
                'type': 'Simple',
                'title': self._card_title,
                'content': self._card_output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': self._reprompt_text
                }
            },
            'shouldEndSession': self._should_end_session
        }

    def _build_response(self, session_attributes):
        """
        Internal helper method to build the Alexa response message
        :param session_attributes:
        :param speechlet_response:
        :return: properly formatted Alexa response
        """
        return {
            'version': '1.0',
            'sessionAttributes': session_attributes,
            'response': self._build_speechlet_response()
        }

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
