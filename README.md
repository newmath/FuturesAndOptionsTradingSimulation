# FuturesAndOptionsTradingSimulation
class libraries, scripts and supporting functions for simulating futures and options trading stratgies

There are currently 2 related projects in this repository: scraping market data from the CME website and simulating trading strategies.  This started out as a data scraper and was expanded to evaluate market opportunities in commodities futures.  So far the simulation only covers historical simluation over available data.  I have started building portfolio risk analytics, but i still need to develop routines for systematically identifying relative value.

Configuration files can be found in the config directory.  This includes files identifying contract terms as well as trading conventions such as option expiry dates and exchange holidays.

The scripts folder contains all of the python code required.  
