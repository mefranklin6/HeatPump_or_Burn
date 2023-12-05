# HeatPump_or_Burn
Useful for setting thresholds in dual-fuel HVAC systems. Uses simple machine learning to find the point at which it is cheaper to use a heat pump.  

Currently only supports natural gas, American units, and single-stage systems.



# How-To:
## 1. Set variables at the top of the script:
- `COST_PER_THERM`: Cost per therm of natural gas in dollars.  Find this on your utility bill
- `COST_PER_KWH` : Cost per Killowatthour (kWh) in dollars.  Find this on your utility bill.  Guess an average price if you have adjustable rate / time of day plans.
- `AFUE` : Efficcency of your furnace.  Find this on your furnace or leave at 80.  In USA, 80 seems to be the standard, but can be as high as 98 for high-end systems.
- `TEMPERATURE_COP_DATA` : This is the measured efficcency of your heat pump system.  Key = Outdoor Temperature, Value = COP measured at that temperature.  This information is hard to find, but you can leave it as it is without worry of being too inaccurate.  These numbers are pulled from labratory tests of the 2022 Carrier Performance 14 and should represent most American style single-stage systems.
- `GRANULARITY` : How accurate you want the results to be.  Ecobee thermostats can only set crossover thresholds in 5 degree increments, so that's the default value.

## 2. Run the program.  
The main function returns the crosspoint you should set your thermostat to.  ex: the temperature that your system will use the furnace when it is below and the heat pump when it is above.  For my ecobee, this is called 'Compressor min outdoor temperature'
