# WRI-Powerplant-Research
Research for Global Powerplant Database project

### Overview ###

The Global Powerplant Database project is working to build an open, global database of powerplant data. It is inspired by projects like [CARMA](http://carma.org), [Enipedia](http://enipedia.tudelft.nl/wiki/Main_Page), [Ventus](http://ventus.project.asu.edu/), and [CoalSwarm](http://coalswarm.org/). A key challenge in powerplant data is estimating missing data, such as annual or monthly generation (in MWh). This repo contains code designed to test various research approaches to improving the estimation methodology for powerplant data.

### Fuel cost and generation ###

Generation is likely to be correlated to fuel cost. Monthly fuel cost and generation data are available for (almost) all US powerplants from EIA, based on Form [EIA-923 data](https://www.eia.gov/electricity/data/eia923/). Unfortunately, these data are structured inconsistently, and need to be restructured and aggregated to allow comparison. This code is designed to do that.

We first obtained complete 2014 data from [EIA-923](https://www.eia.gov/electricity/data/eia923/). We then manually extracted column data about fuel costs from Page 5 (Fuel Receipts and Costs), keeping only the 'YEAR', 'MONTH', 'Plant Id', 'QUANTITY', and 'FUEL_COST' columns, and saved it in CSV format. We next did the same thing for column data about generation from Page 4 (Generator Data), keeping only the 'Plant Id', 'Generator ID', and monthly net generation columns, and saved it in CSV format.

The script read_eia_data.py takes these two CSV files as parameters, reads them, and builds a dictionary of powerplant objects with the plant id as the key. Monthly generation and fuel cost data are read and saved to attributes on the appropriate powerplant object. The script then outputs a CSV file with each powerplant as one row, and monthly fuel cost and generation data as columns.

TODO: Extend to years before 2014.
