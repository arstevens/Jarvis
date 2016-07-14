from ErmrestHandler import ErmrestHandler
import logging
import json
import time

class GelElectrophoresis(object):

	def __init__(self,username,experiment_id,ermrest_handler):
		self.user = username
		self._ermrest = ermrest_handler
		self._table_name = "experiment_data"
		self._catalog = 7
		self._experiment_id = experiment_id
		try:
			self.data = json.loads(self._ermrest.get_data(7,self._table_name,"/user="+
						self.user+"/experiment_id="+str(experiment_id)))
		except:
			self.data = {"experiment_id":experiment_id,"user":self.user,"experiment":None,
					"start_date":None,"end_date":None,"states_completed":None,
					"gel_type":None,"sample_count":None,"power_supply_start_time":None,
					"power_supply_end_time":None}

	def add_item(self, data, item):
		#adds item to a string based list that is held in ermrest.
		if data is None or len(data) == 0:
			data = [item]
		else:
			data = data.split(',')
			data.append(item)

		return ','.join(data)
		
	def reset_user_data(self):
		try:
			self._ermrest.delete_data(self._catalog,self._table_name,"/user="+self.user+
							"/experiment_id="+self._experiment_id)
		except Exception as exc:
			self.logger.error(str(exc))

	def experiment_start_intent(self):
		return "Hello "+self.user+" Which experiment are you going to start"

	def experiment_selection_intent(self, experiment_name):
		#todo: check experiment_name is it allowed?
		self.data['start_date'] = str(time.time())
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'exp-start')
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'exp-selection')
		self.data['experiment_id'] = int(self._experiment_id)
		self.data['experiment'] = experiment_name
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Will it be a Polyacrylamide or Agarose based Gel"

	def experiment_gel_selection_intent(self, gel_type):
		self.data['gel_type'] = gel_type
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'gel-selection')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		self.logger.info("Gel type: "+str(self.data))
		return "Alright "+self.user+" Go ahead and prepare your "+gel_type+" based gel"

	def experiment_gel_mixture_start_intent(self):
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'mixture-start')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Alright "+self.user+", Lets wait for the mixture to boil"

	def experiment_gel_mixture_end_intent(self):
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'mixture-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Alright "+self.user+", cool it for sometime and then load the samples in the wells"

	def experiment_gel_mixture_done_intent(self):
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'mixture-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Go ahead and load the sample in the wells."

	def experiment_loading_gel_start_intent(self):
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'gel-loading-start')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "How many samples you are going to experiment with"

	def experiment_loading_well_count_intent(self, count):
		self.data['sample_count'] = count
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'sample-count')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Go ahead and allocate the samples to individual wells"

	def experiment_loading_sample_assigment_intent(self, sample_type, well_number):
		self.data['samples'] = self.add_item(self.data['samples'], sample_type) 
		self.data['well_numbers'] = self.add_item(self.data['well_numbers'], well_number)
		self.reset_user_data()
		self._ermrest.put_data(self._catalog,self._table_name,self.data)
		return "Copy that"

	def experiment_gel_loading_done_intent(self):
		self.data['states_completed'] = self.add_state(self.data['states_completed'], 'gel-loading-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Go ahead and turn on the power supply"

	def experiment_power_supply_start_intent(self):
    		self.data['power_supply_start_time'] = str(int(time.time()))
		self.data['states_completed'] = self.add_state(self.data['states_completed'], 'power-start')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "You can turn off the supply in 1 minute from now"

	def experiment_power_supply_check_intent(self):
		time_spend = int(time.time()) - int(self.data['power_supply_start_time'])
		if time_spend < 60:
			return 'No, you need to wait ' + str(60 - time_spend) +' more seconds'
		else:
			return "Yes you can"

	def experiment_power_supply_end_intent(self):
		self.data['power_supply_end_time'] = str(int(time.time()))
		self.data['states_completed'] = self.add_state(self.data['states_completed'], 'power-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Roger that"

	def experiment_end_intent(self):
		self.data['end_date'] = str(time.asctime(time.localtime(time.time())))
		self.data['states_completed'] = self.add_state(self.data['states_completed'], 'exp-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return self.user+", your experiment is completed."

	#Need to implement the help intents and create a seperate help center class
