import requests
import json


class ErmrestHandler(object):
	#A class the interacts with the ERMrest web based storage service.
	#Allows you to create schemas,tables etc. and to store and pull data 
	#from the database for further use.
    	def __init__(self, host, username, password):
        	self.host = host
        	self._cookie = {"ermrest": self.get_cookie(username, password)}

    	def get_cookie(self, username, password):
        	r = requests.post('http://'+self.host+'/ermrest/authn/session',
                          	data={'username': username,
                                	'password': password})
        	r.raise_for_status()
        	return r.text[:-1]

    	def create_catalog(self):
		#Returns the catalog id which is needed to fetch data and
		#store data. Also needed to create new schemas and tables.
		#Take note of it.
       		r = requests.post("http://"+self.host+"/ermrest/catalog",cookies=self._cookie)

		r.raise_for_status()
		return json.loads(r.text)

    	def create_schema(self,catalog_id, name):
       		r = requests.post("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+
				"/schema/"+name,cookies=self._cookie)

		r.raise_for_status()

    	def create_table(self,catalog_id,schema_name, table):
		#Table item must be in the proper json format. 
		#Table must also be of python dict type
		#For more information go to: 
		#https://github.com/informatics-isi-edu/ermrest/blob/master/api-doc/model/rest.md
		r = requests.post("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+
				"/schema/"+schema_name+"/table",json=table,cookies=self._cookie)	
	
		r.raise_for_status()

	def delete_catalog(self,catalog_id):
		r = requests.delete("http://"+self.host+"/ermrest/catalog/"+str(catalog_id),
					cookies=self._cookie)

		r.raise_for_status()
		
	def delete_schema(self,catalog_id,schema_name):
		r = requests.delete("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+
					"/schema/"+schema_name,cookies=self._cookie)

		r.raise_for_status()

	def delete_table(self,catalog_id,schema_name,table_name):
		r = requests.delete("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+
					"/schema/"+schema_name+"/table/"+table_name,cookies=self._cookie)

		r.raise_for_status()

    	def get_data(self, catalog_id, table_name, user_name):
        	r = requests.get("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+"/entity/"+
                         	table_name+"/user="+user_name, cookies=self._cookie)
        	return json.loads(r.text)

	def get_table_data(self,catalog_id,table_name):
		r = requests.get("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+"/entity/"+
				table_name,cookies=self._cookie)
		return json.loads(r.text)

    	def delete_data(self, catalog_id, table_name, user_name):
        	r = requests.delete("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+"/entity/"+
                         	table_name+"/user="+user_name, cookies=self._cookie)

		r.raise_for_status()	

    	def put_data(self, catalog_id, table_name, data):
		#data must be in a python dict type and in the correct table format.
		#see the README for more information.
        	data = [data]
        	r = requests.put("http://"+self.host+"/ermrest/catalog/"+str(catalog_id)+"/entity/"+table_name,
                         	json=data, cookies=self._cookie)

        	r.raise_for_status()

