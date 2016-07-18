from ErmrestHandler import ErmrestHandler

#resets all the data that is stored in the ermrest catalog for Jarvis
def reset():
	e = ErmrestHandler("ec2-54-172-182-170.compute-1.amazonaws.com","root","root")

	try:
		e.delete_data(7,"experiment_data")
	except:
		pass
	try:
		e.delete_data(7,"step_completed")
	except:
		pass
	try:
		e.delete_data(7,"session_info")
	except:
		pass

	e.put_data(7,"session_info",{"user":None,"jarvis_response":None,"current_experiment_id":None})
	e.put_data(7,"step_completed",{"completed_step":None})
	print("Success")


reset()
