from ErmrestHandler import ErmrestHandler
from num2words import num2words
import json
import time

class GelElectrophoresis(object):

	def __init__(self,username,experiment_id,ermrest_handler):
		#Contains all the methods to run for experiment intents.
		#Returns the text response and writes data to ermrest.
		self.user = username
		self._ermrest = ermrest_handler
		self._table_name = "experiment_data"
		self._catalog = 7
		self._experiment_id = experiment_id
		try:
			self.data = json.loads(json.dumps(self._ermrest.get_data(7,self._table_name,"/user="+
						self.user+"/experiment_id="+str(experiment_id))[0]))
		except Exception as exc:
			print("grab data error:"+str(exc))
			self.data = {"experiment_id":experiment_id,"user":self.user,"experiment":None,
					"start_date":None,"end_date":None,"states_completed":None,
					"gel_type":None,"sample_count":None,"power_supply_start_time":None,
					"power_supply_end_time":None,"samples":None,"well_numbers":None}

	def add_item(self, data, item):
		#adds item to a string based list that is held in ermrest.
		#Lists that use add_item: states_completed,samples,well_numbers
		if data is None or len(data) == 0:
			data = [item]
		else:
			data = data.split(',')
			data.append(item)

		return ','.join(data)
		
	def item_exists(self,data,item):
		if data is None or len(data) == 0:
			return False
		
		data_list = data.split(',')

		if item in data_list:
			return True
		return False

	def reset_user_data(self):
		#resets the experiment data so their are no duplicate lists
		try:
			self._ermrest.delete_data(self._catalog,self._table_name,"/user="+self.user+
							"/experiment_id="+str(self._experiment_id))
		except Exception as exc:
			print("reset user data error:"+str(exc))

	def experiment_start_intent(self):
		return "Hello "+self.user+" Which experiment are you going to start"

	def experiment_selection_intent(self, experiment_name):
		#todo: check experiment_name is it allowed?
		self.data['start_date'] = str(time.asctime(time.localtime(time.time())))
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
		return "Alright "+self.user+", Go ahead and prepare your "+gel_type+" based gel"

	def experiment_gel_mixture_start_intent(self):
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'mixture-start')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Alright "+self.user+", Lets wait for the mixture to boil"

	def experiment_gel_mixture_end_intent(self):
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'mixture-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Alright "+self.user+", cool it for some time and then load the samples in to the wells"

	def experiment_loading_gel_start_intent(self):
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'gel-loading-start')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "How many samples are you going to experiment with"

	def experiment_loading_well_count_intent(self, count):
		self.data['sample_count'] = count
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'sample-count')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "Go ahead and allocate the samples in to individual wells"

	def experiment_loading_sample_assignment_intent(self, sample_type, well_number):
		#checks if the well or sample is already assigned
		print("in experiment loading samp assign intent")
		amount_of_samples_used = 0
		sample_count = 9999
		if (self.data['samples']):
			amount_of_samples_used = len(self.data['samples'].split(","))
			sample_count = int(self.data['sample_count'])
		
		if (amount_of_samples_used >= sample_count):
			print("too big!")
			return "You have already loaded all the samples. Please continue the experiment."

		elif (self.item_exists(self.data['samples'],sample_type) == False and 
			self.item_exists(self.data['well_numbers'],str(well_number)) == False):
			print("evaluated true")
			self.data['samples'] = self.add_item(self.data['samples'], sample_type) 
			print("assigned samples")
			self.data['well_numbers'] = self.add_item(self.data['well_numbers'], str(well_number))
			print("assinged well numbers")
			self.reset_user_data()
			print("reset")
			self._ermrest.put_data(self._catalog,self._table_name,self.data)
			print("put data")
			return "Copy that. Sample {} has been assigned to well {}".format(sample_type,num2words(int(well_number)))
		
		else:
			print("evaluated false")
			return "The well or sample you provided me is already in use. Please choose a different one"

	def experiment_gel_loading_done_intent(self):
		print("in gel loading intent")
		amount_of_samples_used = len(self.data['samples'].split(","))
		print("samples used: "+str(amount_of_samples_used))
		amount_of_samples_left = num2words(self.data['sample_count']-amount_of_samples_used)
		print("samples left:"+amount_of_samples_left)
		#checks if you have any unassigned samples
		if (amount_of_samples_used == self.data['sample_count']):
			print("in equals")
			self.data['states_completed'] = self.add_item(self.data['states_completed'], 'gel-loading-end')
			self.reset_user_data()
			self._ermrest.put_data(self._catalog, self._table_name, self.data)
			return "Go ahead and turn on the power supply"
		print("not finished")
		return "You are yet to assign {} samples to wells. Please finish assigning the samples".format(amount_of_samples_left)

	def experiment_power_supply_start_intent(self):
    		self.data['power_supply_start_time'] = str(int(time.time()))
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'power-start')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return "You can turn off the supply in 1 minute from now"

	def experiment_power_supply_check_intent(self):
		time_spend = int(time.time()) - int(self.data['power_supply_start_time'])
		if time_spend < 60:
			return 'No, you need to wait ' + str(num2words(60 - time_spend)) +' more seconds'
		else:
			return "Yes you can"

	def experiment_power_supply_end_intent(self):
		self.data['power_supply_end_time'] = str(int(time.time()))
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'power-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)		
		time_spent = int(time.time()) - int(self.data['power_supply_start_time'])

		if time_spent > 60:
			return "Roger that, Don't forget to record your findings"

		return "You turned the power supply off too early"

	def experiment_end_intent(self):
		self.data['end_date'] = str(time.asctime(time.localtime(time.time())))
		self.data['states_completed'] = self.add_item(self.data['states_completed'], 'exp-end')
		self.reset_user_data()
		self._ermrest.put_data(self._catalog, self._table_name, self.data)
		return self.user+", your experiment is completed."