# read_eia_data.py
"""
Read EIA-derived CSV files with fuel cost information.
: param: fuel_cost_file: Filename of fuel cost data file
: param: generation_file: Filename of generation data file
: param: save_filename: Filename to save resulting database
"""

import csv
import argparse

class power_plant(object):
	# Class to hold data for an individual power plant. 
	# Monthly generation and fuel cost are stored in dictionaries, with keys "YYYY.MM"
	plant_count = 0
	def __init__(self,plant_id):
		self.plant_id = plant_id
		self.monthly_fuel_cost = {}
		self.monthly_generation_MWh = {}
		power_plant.plant_count += 1

# main

parser = argparse.ArgumentParser(description='Read EIA-derived CSV files and extract monthly fuel cost and generation by plant.')
parser.add_argument('fuel_cost_file', type=str, help='CSV file with fuel costs.')
parser.add_argument('generation_file', type=str, help='CSV file with generation data.')
parser.add_argument('save_filename', type=str, help='Filename to save results.')
args = parser.parse_args()

# create dictionary for power plant objects
power_plant_dict = {}

### READ IN DATA FROM FUEL COST FILE ###

with open(args.fuel_cost_file, 'rU') as csvfile:
	datareader = csv.reader(csvfile)
	headers = datareader.next()

	# identify columns
	year_col = headers.index("YEAR")
	month_col = headers.index("MONTH")
	plant_id_col = headers.index("Plant Id")
	fuel_cost_col = headers.index("FUEL_COST")

	# read columns
	for row in datareader:
		year = row[year_col]			# read as string
		month = row[month_col]			# read as string
		plant_id = row[plant_id_col]	# read as string

		# convert fuel cost to float
		fuel_cost_string = row[fuel_cost_col]	
		try:
			fuel_cost = float(row[fuel_cost_col].replace(",",""))	# strip commas
		except:
			fuel_cost = 0.0

		# find power plant in power plant dictionary, or create and add if new
		if plant_id in power_plant_dict:
			plant_obj = power_plant_dict[plant_id]
		else:
			plant_obj = power_plant(plant_id)
			power_plant_dict[plant_id] = plant_obj

		# add monthly fuel cost to power plant object; key for dict is YYYY.MM
		# note that because of multiple generators per plant, we need to use +=
		new_key = "{0}.{1}".format(year.zfill(4),month.zfill(2))
		if plant_obj.monthly_fuel_cost.has_key(new_key):
			plant_obj.monthly_fuel_cost[new_key] += fuel_cost
		else:
			plant_obj.monthly_fuel_cost[new_key] = fuel_cost

### READ IN DATA FROM GENERATION FILE ###
# Note that this is structured differently than the fuel cost file, so read is different
# Months are in separate columns on the same row, not individual rows

month_column_names = ["Net Generation\nJanuary", "Net Generation\nFebruary", "Net Generation\nMarch", "Net Generation\nApril", "Net Generation\nMay", "Net Generation\nJune", "Net Generation\nJuly", "Net Generation\nAugust", "Net Generation\nSeptember", "Net Generation\nOctober", "Net Generation\nNovember", "Net Generation\nDecember"]
month_column_indices = []

with open(args.generation_file, 'rU') as csvfile:
	datareader = csv.reader(csvfile)
	headers = datareader.next()

	# identify columns
	year_col = headers.index("YEAR")
	plant_id_col = headers.index("Plant Id")
	for month in month_column_names:
		month_column_indices.append(headers.index(month))

	# read columns
	for row in datareader:
		year = row[year_col]			# read as string
		plant_id = row[plant_id_col]	# read as string

		# find power plant in power plant dictionary, or create and add if new
		if plant_id in power_plant_dict:
			plant_obj = power_plant_dict[plant_id]
		else:
			plant_obj = power_plant(plant_id)
			power_plant_dict[plant_id] = plant_obj

		# for each monthly column, convert generation to float
		month_number = 1
		for month_col in month_column_indices:
			generation_string = row[month_col]	
			try:
				generation = float(row[month_col].replace(",",""))	# strip commas
			except:
				generation = 0.0

			# add monthly generation to power plant object; key for dict is YYYY.MM
			# note that because of multiple generators per plant, we need to use +=
			new_key = "{0}.{1}".format(year.zfill(4),str(month_number).zfill(2))
			if plant_obj.monthly_generation_MWh.has_key(new_key):
				plant_obj.monthly_generation_MWh[new_key] += fuel_cost
			else:
				plant_obj.monthly_generation_MWh[new_key] = fuel_cost

			month_number += 1


# report number of power plants found
print("Found {0} power plants".format(power_plant.plant_count))

### OUTPUT ###

# build list of headers
yyyy_mm_list = []
for year in ['2014']:
	for month in range(1,13):		# remember range goes to one less than second param
		yyyy_mm_list.append("{0}.{1}".format(year,str(month).zfill(2)))

header_list = ['Plant_Id']
# build fuel cost headers
for val in yyyy_mm_list:
	header_list.append('fuel_cost_' + val)
# build generation headers
for val in yyyy_mm_list:
	header_list.append('generation_MWh_' + val)

with open(args.save_filename, 'w') as csvfile:
	datawriter = csv.writer(csvfile,delimiter = ",")
	# write the header row
	datawriter.writerow(header_list)

	# write each power plant as a new row
	for key in power_plant_dict:
		plant = power_plant_dict[key]
		write_list = [plant.plant_id]
		# build fuel cost values
		for key in yyyy_mm_list:
			if plant.monthly_fuel_cost.has_key(key):
				formatted_val = "{:.2f}".format(plant.monthly_fuel_cost[key])
			else:
				formatted_val = "0"
			write_list.append(formatted_val)
		# build generation values
		for key in yyyy_mm_list:
			if plant.monthly_generation_MWh.has_key(key):
				formatted_val = "{:.2f}".format(plant.monthly_generation_MWh[key])
			else:
				formatted_val = "0"
			write_list.append(formatted_val)
		datawriter.writerow(write_list)


