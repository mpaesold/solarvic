# solarvic
The intent of this project is to model the likely value of rooftop/small-scale solar for a single project.
It takes as input 
1. the array location (latitude, longitude) 
2. the array details: capacity, azimuth, and tilt  of the various solar arrays (note that it is assumed that solar arrays will be fixed).
3. Calendar of which days are working days vs non-working days (check: how are we going to do this? It shouldn't be exclusive to schools)
4. Hourly power consumption for a year (check: do we handle leap years? Should be OK - just need holiday calendar to be aligned with power consumption)
5. Electricity price ($/kWh) for both consumption from the grid, and feeding into the grid 

Method
1. The various arrays are modelled using the NREL api to calculate representative daily power production for the combined set of arrays for each month of the year
2. The calendar is matched with the consumption to model consumption for 2 typical days per month - a working day, and a non-working day.
3. Net power demand is calculated per hour of the day, per day type for each month of the year
4. Potential annual savings are calculated based on reduced consumption and profit from selling to the grid.

Next Steps
1. Calendar of working/non-working days needn't be restricted to schools. Have some defaults. Store holidays when entered by users. So if a school in France enters values, next time a school in France is entered, we can suggest a calendar. Would need to be smart enough to record how far away it is from previous school. Suggest nearer things first.
2. Store power production results to speed up performance (not have to query NREL) and reduce demand. NREL free user id is limited to 1000 queries per day.
3. For feeding in to the grid, there is more than one way to skin a cat! Net metering is quite common in the USA. I believe that this is like, up to a point, you are allowed to push power back into the grid to use later. But you can only carry it over for a limited time e.g. 1 month. Can also limit feed-in to grid to a max power, or say that will only pay for the first n kW per day.
4. Demand Charges - for more industrial users, there is often a "demand charge" which is paid per month/quarter and is based on $/kW - not $/kWh. It is a charge for the peak load in the period.
5. Modelling value of batteries - this is starting to get a bit dicey, especially if we are using 12 standard days of weather. Much of the value of batteries would be to handle the variation between 1 day and the next.
