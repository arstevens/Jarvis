__author__ = 'anurag'
from ErmrestHandler import ErmrestHandler
import logging
import time

class GelElectrophoresis(object):
    def __init__(self, user):
        #todo: get all info for the user from db
        self.user = user
        self._ermrest = ErmrestHandler('ec2-54-172-182-170.compute-1.amazonaws.com', 'root', 'root')
        self._table_name = 'sample7'
        try:
            self.data = self._ermrest.get_data(1, self._table_name, self.user)[0]
        except Exception as e:
            self.data = {u'sample_count': None, u'end_date': None, u'gel_type': None, u'power_supply_start_time': None, u'states_completed': None, u'experiment': None, u'user': user, u'power_supply_end_time': None, u'start_date': None}
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info("Init: "+str(self.data))
        self._state_order = ['exp-start', 'exp-selection', 'gel-selection', 'mixture-start', 'mixture-end',
                             'gel-loading-start', 'sample-count', 'gel-loading-end', 'power-start',
                             'power-end', 'exp-end']

    def get_next_state_info(self):
        state = self.data['states_completed']
        if state is None or len(state) == 0:
            return 'You can start an experiment'

        state = state.split(',')
        last_state = state[len(state)-1]
        if last_state == 'gel-loading-end':
            return 'You can start the power supply for the chamber'
        if last_state == 'exp-selection':
            return 'You can select the gel type for electrophoresis experiment. Will it be a Polyacrylamide or Agarose based Gel'

        return "Help system is not completed yet"

    def add_state(self, state, new_state):
        if state is None or len(state) == 0:
            state = [new_state]
        else:
            state = state.split(',')
            state.append(new_state)

        return ','.join(state)


    def experiment_start_intent(self):
        #todo: check if not other experiment is going on for this user
        self.data['user'] = self.user
        self.data['start_date'] = str(int(time.time()))
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'exp-start')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Hello "+self.user+" Which experiment are you going to start"

    def experiment_selection_intent(self, experiment_name):
        #todo: check experiment_name is it allowed?
        #todo: handler for state validation
        if 'exp-start' not in self.data['states_completed']:
            return 'Hmmm.. seems like you did not start an experiment yet. Please let me know which experiment you want to start'

        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'exp-selection')
        self.data['experiment'] = experiment_name
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Will it be a Polyacrylamide or Agarose based Gel"

    def experiment_get_selection_intent(self, gel_type):
        if 'exp-start' not in self.data['states_completed'] or 'exp-selection' not in self.data['states_completed']:
            return 'Hmmm.. seems like you did not start an experiment'

        self.data['gel_type'] = gel_type
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'gel-selection')
        self._ermrest.put_data(1, self._table_name, self.data)
        self.logger.info("Gel type: "+str(self.data))
        return "Alright "+self.user+" Go ahead and prepare your "+gel_type+" based gel"

    def experiment_get_mixture_start_intent(self):
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'mixture-start')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Alright "+self.user+", Lets wait for the mixture to boil"

    def experiment_get_mixture_end_intent(self):
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'mixture-end')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Alright "+self.user+", cool it for sometime and then load the samples in the wells"

    def experiment_get_mixture_done_intent(self):
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'mixture-end')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Go ahead and load the sample in the wells."

    def experiment_loading_gel_start_done_intent(self):
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'gel-loading-start')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "How many samples you are going to experiment with"

    def experiment_get_loading_well_count_intent(self, count):
        self.data['sample_count'] = count
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'sample-count')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Go ahead and allocate the samples to individual wells"

    def experiment_get_loading_sample_assigment_intent(self, sample_type, well_number):
        return "Copy that"

    def experiment_get_loading_done_intent(self):
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'gel-loading-end')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Go ahead and turn on the power supply"

    def experiment_power_supply_start_intent(self):
        self.data['power_supply_start_time'] = str(int(time.time()))
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'power-start')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "You can turn off the supply in 1 minute from now"

    def experiment_power_supply_check_intent(self):
        time_spend = int(time.time()) - int(self.data['power_supply_start_time'])
        if time_spend < 60:
            return 'No, you need to wait ' + str(60 - time_spend) +' seconds more'
        else:
            return "Yes you can"

    def experiment_power_supply_end_intent(self):
        self.data['power_supply_end_time'] = str(int(time.time()))
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'power-end')
        self._ermrest.put_data(1, self._table_name, self.data)
        return "Roger that"

    def experiment_end_intent(self):
        self.data['end_date'] = str(int(time.time()))
        self.data['states_completed'] = self.add_state(self.data['states_completed'], 'exp-end')
        self._ermrest.put_data(1, self._table_name, self.data)
        return self.user+", your experiment is completed."

    def experiment_help_intent(self):
        return self.get_next_state_info()

    def experiment_status_check_intent(self):
        return self.user+", this is what you have done so far."
