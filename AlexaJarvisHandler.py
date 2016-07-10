from AlexaBaseHandler import AlexaBaseHandler
from GelElectrophoresis import GelElectrophoresis
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
        name = self._get_intent_name(request)
        session_attributes = AlexaBaseHandler._get_session_attribute(session)

        if 'slots' not in self._get_intent(request):
            return self._test_response("No user name provided")

        slots = self._get_intent(request)['slots']
        experiment = GelElectrophoresis(slots['UserName']['value'])

        if name == 'ExperimentStartIntent':
            self._speech_output = experiment.experiment_start_intent()
        elif name == 'ExperimentSelectionIntent':
            self._speech_output = experiment.experiment_selection_intent(slots['ExperimentName']['value'])
        elif name == 'ExperimentGelSelectionIntent':
            self._speech_output = experiment.experiment_get_selection_intent(slots['GelName']['value'])
        elif name == 'ExperimentGelMixtureStartIntent':
            self._speech_output = experiment.experiment_get_mixture_start_intent()
        elif name == 'ExperimentGelMixtureEndIntent':
            self._speech_output = experiment.experiment_get_mixture_end_intent()
        elif name == 'ExperimentGelMixtureDoneIntent':
            self._speech_output = experiment.experiment_get_mixture_done_intent()
        elif name == 'ExperimentLoadingGelStartIntent':
            self._speech_output = experiment.experiment_loading_gel_start_done_intent()
        elif name == 'ExperimentLoadingWellCountIntent':
            self._speech_output = experiment.experiment_get_loading_well_count_intent(slots['WellCount']['value'])
        elif name == 'ExperimentLoadingSampleAssignmentIntent':
            self._speech_output = experiment.experiment_get_loading_sample_assigment_intent(slots['SampleType']['value'], slots['WellNumber']['value'])
        elif name == 'ExperimentLoadingGelDoneIntent':
            self._speech_output = experiment.experiment_get_loading_done_intent()
        elif name == 'ExperimentPowerSupplyStartIntent':
            self._speech_output = experiment.experiment_power_supply_start_intent()
        elif name == 'ExperimentPowerSupplyCheckIntent':
            self._speech_output = experiment.experiment_power_supply_check_intent()
        elif name == 'ExperimentPowerSupplyEndIntent':
            self._speech_output = experiment.experiment_power_supply_end_intent()
        elif name == 'ExperimentEndIntent':
            self._speech_output = experiment.experiment_end_intent()
        elif name == 'ExperimentHelpIntent':
            self._speech_output = experiment.experiment_help_intent()
        elif name == 'ExperimentStatusCheckIntent':
            self._speech_output = experiment.experiment_status_check_intent()

        return self._build_response(session_attributes)

    def on_session_ended(self, request, session):
        session_attributes = self._get_session_attribute(session)
        self._speech_output = "on session end"
        return self._build_response(session_attributes)

