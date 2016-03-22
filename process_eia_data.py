# process_eia_data.py
"""
SUMMARY:

Read EIA-derived CSV files with fuel cost and generation information and output combined data to CSV file.
: param: fuel_cost_file: Filename of fuel cost data file
: param: generation_file: Filename of generation data file
: param: save_filename: Filename to save resulting database
: param: year: Year of data being processed

NOTES:

1. EIA data are from EIA-923. Zipped Excel files are available here:

2014: https://www.eia.gov/electricity/data/eia923/xls/f923_2014.zip
2013: https://www.eia.gov/electricity/data/eia923/xls/f923_2013.zip
2012: https://www.eia.gov/electricity/data/eia923/xls/f923_2012.zip
2011: https://www.eia.gov/electricity/data/eia923/xls/f923_2011.zip
2010: https://www.eia.gov/electricity/data/eia923/xls/f923_2010.zip
2009: https://www.eia.gov/electricity/data/eia923/xls/f923_2009.zip
2008: https://www.eia.gov/electricity/data/eia923/xls/f923_2008.zip

2. Prior to 2008, the forms and format changed, so this code does not handle those years.

3. Before running this code, the Excel files were processed as follows: Using "EIA923_Schedules_2_3_4_5_M_12_20XX_Final_Revision.xlsx", save "Page 4" as "EIA923_20XX_generation.csv" and "Page 5" as "EIA923_20XX_fuel_cost.csv".

4. The EIA923 forms break out each generator at each plant.

5. This code reads the separate CSV files for fuel cost and generation, aggregates monthly data up to the plant level (summing each generator) and then writes a CSV file with the monthly data (for generation and fuel cost) for each plant on a single row.

"""

import csv
import argparse
from power_plant_class import PowerPlant

# main

parser = argparse.ArgumentParser(description='Read EIA-derived CSV files and extract monthly fuel cost and generation by plant.')
parser.add_argument('fuel_cost_file', type=str, help='CSV file with fuel costs.')
parser.add_argument('generation_file', type=str, help='CSV file with generation data.')
parser.add_argument('save_filename', type=str, help='Filename to save results.')
parser.add_argument('year', type=str, help='Year of data being processed.')

args = parser.parse_args()

# create dictionary for power plant objects
power_plant_dict = {}

### READ IN DATA FROM FUEL COST FILE ###
# Data for each plant/generator/month combination are on a separate row.

with open(args.fuel_cost_file, 'rU') as csvfile:
	datareader = csv.reader(csvfile)
	headers = datareader.next()

	# skip leading rows with general information
	while "Plant Id" not in headers:
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
		plant_id = int(row[plant_id_col])	# read as int

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
			plant_obj = PowerPlant(plant_id)
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

month_column_names = ["Net Generation January", "Net Generation February", "Net Generation March", "Net Generation April", "Net Generation May", "Net Generation June", "Net Generation July", "Net Generation August", "Net Generation September", "Net Generation October", "Net Generation November", "Net Generation December"]

month_column_indices = []

with open(args.generation_file, 'rU') as csvfile:
	datareader = csv.reader(csvfile)
	headers = datareader.next()

	# skip leading rows with general information
	while "Plant Id" not in headers:
		headers = datareader.next()

	# identify columns
	headers = [h.replace("\n"," ") for h in headers]	# strip newlines
	year_col = headers.index("YEAR")
	plant_id_col = headers.index("Plant Id")
	for month in month_column_names:
		month_column_indices.append(headers.index(month))

	# read columns
	for row in datareader:
		year = row[year_col]			# read as string
		plant_id = int(row[plant_id_col])	# read as int

		# find power plant in power plant dictionary, or create and add if new
		if plant_id in power_plant_dict:
			plant_obj = power_plant_dict[plant_id]
		else:
			plant_obj = PowerPlant(plant_id)
			power_plant_dict[plant_id] = plant_obj

		# for each monthly column, convert generation to float
		for month_number_zero_base,month_col in enumerate(month_column_indices):
			generation_string = row[month_col]	
			try:
				generation = float(row[month_col].replace(",",""))	# strip commas
			except:
				generation = 0.0

			# add monthly generation to power plant object; key for dict is YYYY.MM
			# note that because of multiple generators per plant, we need to use +=
			# remember that enumerate() is zero-indexed
			new_key = "{0}.{1}".format(year.zfill(4),str(month_number_zero_base+1).zfill(2))
			if plant_obj.monthly_generation_MWh.has_key(new_key):
				plant_obj.monthly_generation_MWh[new_key] += generation
			else:
				plant_obj.monthly_generation_MWh[new_key] = generation


# report number of power plants found
print("Found {0} power plants".format(PowerPlant.plant_count))

### OUTPUT ###

# build list of headers
yyyy_mm_list = []
for year in [args.year]:
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
	for key in sorted(power_plant_dict):
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


