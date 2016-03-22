class PowerPlant(object):
	# Class to hold data for an individual power plant. 
	# Monthly generation and fuel cost are stored in dictionaries, with keys "YYYY.MM"
	plant_count = 0
	def __init__(self,plant_id):
		self.plant_id = plant_id
		self.monthly_fuel_cost = {}
		self.monthly_generation_MWh = {}
		PowerPlant.plant_count += 1
