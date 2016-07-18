#=======Imports==========================
from ErmrestHandler import ErmrestHandler
from num2words import num2words
import time
#=======Class============================

class DataRetrieval(object):
	
	def __init__(self,ermrest,experiment_id):
		#gets data that the user requests and returns the proper response
		self._ermrest = ermrest
		self._experiment_id = int(experiment_id) 
		self._username = self._get_session_data("user")
		self._experiment_query = "/user="+self._username+"/experiment_id="+str(self._experiment_id)
	
	def get_experiment_id_intent(self):
		#returns the response for the GetExperimentIdIntent
		return "The experiment id of the experiment your working on is "+num2words(self._experiment_id)
	
	def get_start_date_intent(self):
		#gets the start date of the experiment and constructs response
		start_date = self._get_experiment_data("start_date")
		speakable_time = self._epoch_to_time(start_date)
		return "You started this experiment on "+speakable_time
	
	def get_end_date_intent(self):
		#gets the end date of the experiment and constructs response
		end_date = self._get_experiment_data("end_date")
		speakable_time = self._epoch_to_time(end_date)
		return "You ended this experiment on "+speakable_time
	
	def get_sample_count_intent(self):
		#gets the amount of samples experimented with and constructs response
		sample_count = self._get_experiment_data("sample_count")
		speakable_count = num2words(int(sample_count))
		return "You experimented with "+speakable_count+" samples"
	
	def get_well_sample_assignment_intent(self,well_number):
		#gets the sample that was assigned to the well number given and constructs a response
		well_numbers = self._get_experiment_data("well_numbers")
		samples = self._get_experiment_data("samples")
		well_index = well_numbers.find(str(well_number))
		assigned_sample = samples[well_index]
		speakable_well = num2words(int(well_number))
		return "Well number "+speakable_well+" is assigned to sample "+assigned_sample
	
	def get_sample_well_assignment_intent(self,sample):
		#gets well assigned to sample that was provided and constructs response
		well_numbers = self._get_experiment_data("well_numbers")
		samples = self._get_experiment_data("samples")
		sample_index = samples.find(sample)
		assigned_well = num2words(int(well_numbers[sample_index]))
		return "Sample "+sample+" was assigned to well number "+assigned_well
	
	def _get_experiment_data(self,column):
		#gets data from the experiment_data table 
		return_data = None
		query = "/user="+self._username+"/experiment_id="+str(self._experiment_id)
		raw_data = self._ermrest.get_data(7,"experiment_data",query)

		if (raw_data):
			return_data = raw_data[0][column]
		
		return return_data
	
	def _get_session_data(self,column):
		#gets data from the session_info table
		return_data = None
		raw_data = self._ermrest.get_data(7,"session_info")

		if (raw_data):
			return_data = raw_data[0][column]

		return return_data
	
	def _epoch_to_time(self,timestamp):
		#creates and returns a speakable version of the date for alexa
		time_date = timestamp.split(" ") 
		new_date = ""

		#Adds day of the week to new_date
		if time_date[0] == "Mon":
			new_date += "Monday "
		elif time_date[0] == "Tue":
			new_date += "Tuesday "
		elif time_date[0] == "Wed":
			new_date += "Wednsday "
		elif time_date[0] == "Thu":
			new_date += "Thursday "
		elif time_date[0] == "Fri":
			new_date += "Friday "
		elif time_date[0] == "Sat":
			new_date += "Saturday "
		elif time_date[0] == "Sun":
			new_date += "Sunday "
		
		#Adds month to new_date
		if time_date[1] == "Jan":
			new_date += "January "
		elif time_date[1] == "Feb":
			new_date += "February "
		elif time_date[1] == "Mar":
			new_date += "March "
		elif time_date[1] == "Apr":
			new_date += "April "
		elif time_date[1] == "May":
			new_date += "May "
		elif time_date[1] == "Jun":
			new_date += "June "
		elif time_date[1] == "Jul":
			new_date += "July "
		elif time_date[1] == "Aug":
			new_date += "August "
		elif time_date[1] == "Sep":
			new_date += "September "
		elif time_date[1] == "Oct":
			new_date += "October "
		elif time_date[1] == "Nov":
			new_date += "November "
		elif time_date[1] == "Dec":
			new_date += "December "

		#Adds day to new_date
		new_date += num2words(int(time_date[2]))+" "
		
		#Adds year to new_date
		new_date += num2words(int(time_date[4]))+" "
		
		#Adds time to new_date
		date_time = time_date[3].split(":")
		for number in range(len(date_time)):
			date_time[number] = num2words(int(date_time[number]))
		date_time = date_time[:-1]
		new_date += " ".join(date_time)

		#return
		return new_date
