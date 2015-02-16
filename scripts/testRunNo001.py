#!/opt/local/bin/python  
#
# Test run for option-derived futures trading strategy 

#STANDARD PYTHON MODULES
from datetime import datetime, time, date
timeStart = datetime.now()  

import pickle   
print 'pickly loaded',str((datetime.now() - timeStart).seconds),'seconds'      

#CUSTOM MODULES  
from Portfolio import * 
from Future import *
from FutureOption import *  
from FuturesHashConvert import * 
from interpolation import *
from deltaHedgePortfolio import *
print 'loaded custom modules',str((datetime.now() - timeStart).seconds),'seconds'     
      
#DEFINE TARGET COMMODITY, REFERENCE FUTURE OPTION AND STRATEGY PARAMETERS 
commodity = 'C'  
contract = '201403'
contract_size = GetContractQuantityByTicker(commodity)
quantity = 100
strike_round = 1
optionModel = 'lognormal'
longHedgeTime = 3
shortHedgeTime = 1
startDate = date(2013,8,30)
endDate = date(2099,12,31)  
print 'parameters set',str((datetime.now() - timeStart).seconds),'seconds'       

#LOAD FUTURES AND VOLS AND RATES    
dbfile = open('../db/tsFutures.dat','r')   
FUTURESERIES = pickle.load(dbfile)  
dbfile.close()  
print 'Futures Curves loaded',str((datetime.now() - timeStart).seconds),'seconds'       
dbfile = open('../db/tsVols.dat','r')    
VOLSERIES = pickle.load(dbfile)  
dbfile.close()  
print 'Vol Surfaces loaded',str((datetime.now() - timeStart).seconds),'seconds'       
dbfile = open('../db/tsDFCurves.dat','r')
RATES = pickle.load(dbfile)
dbfile.close()
print 'DF curves loaded',str((datetime.now() - timeStart).seconds),'seconds'       

#CONVERT FUTURES HASHES TO SCENARIO HASHES  
CURVES = dict()  
ConvertFuturesHashToCurvesHash(FUTURESERIES,CURVES,startDate,endDate)  
VOLS = dict()  
ConvertFuturesHashToCurvesHash(VOLSERIES,VOLS,startDate,endDate)  
print 'Market data converted to scenarios',str((datetime.now() - timeStart).seconds),'seconds'       

refDates = CURVES.keys()  
refDates.sort()  

#START WITH FIRST DATE AFTER START DATE
refDate = refDates[0]
SCEN = dict()
BuildHistoricalScenario(refDate,SCEN,CURVES,VOLS,RATES)

#BUILD PORTFOLIO OF LONG AND SHORT ATM CALL OPTIONS 
SHORT_CALL = Portfolio('Short Call')    
LONG_CALL = Portfolio('Long Call')   
PORT = Portfolio('Combined')  

forward = CURVES[refDate][commodity][contract]['Close']  
strike = float(round(forward / strike_round,0)) * strike_round   
#print forward, strike  

#GET EXPIRY DATES FOR RELEVANT CONTRACT IN SIMILAR WAY AS DONE WHEN CALCULATING THE VOL SURFACES  
optYear = int(contract[:4])
optMonth = int(contract[5:])
optExpDate = opt_exp_dates()[commodity][optYear][optMonth]  

#CREATE INITIAL OPTION POSITIONS
LC = FutureOption(commodity,contract,optExpDate,strike,1,quantity,contract_size,optionModel)
SC = FutureOption(commodity,contract,optExpDate,strike,1,(-1 * quantity),contract_size,optionModel)

#ADD OPTIONS TO SUBPORTFOLIOS
LONG_CALL.Trades.append(LC)
SHORT_CALL.Trades.append(SC)
#ADD SUBPORTFOLIOS TO PORTFOLIO  
PORT.Trades.append(LONG_CALL)
PORT.Trades.append(SHORT_CALL)

#DELTA HEDGE PORTFOLIOS TO START
DeltaHedgePortfolio(LONG_CALL,SCEN)
DeltaHedgePortfolio(SHORT_CALL,SCEN)  

#ANALYZE EXISTING PORTFOLIO TO TRACK P&L AND RISK  
longNPV = LONG_CALL.NPV(SCEN)  
shortNPV = SHORT_CALL.NPV(SCEN)
netNPV = PORT.NPV(SCEN)  
LONG_DELTAS = dict()  
SHORT_DELTAS = dict()  
PORT_DELTAS = dict()  
LONG_CALL.Deltas(SCEN,LONG_DELTAS)  
SHORT_CALL.Deltas(SCEN,SHORT_DELTAS)  
PORT.Deltas(SCEN,PORT_DELTAS)
longDelta = LONG_DELTAS[commodity][contract]  
shortDelta = SHORT_DELTAS[commodity][contract]  
netDelta = PORT_DELTAS[commodity][contract]  

strOut = 'refDate,Forward,Long NPV,Long Delta,Long Trades,Short NPV,Short Delta,Short Trades,Net NPV,Net Delta'  
strOut += '\n' + refDate.isoformat() + "," + str(forward) + ',' + str(longNPV) + ',' + str(longDelta) + ',' + str(LONG_CALL.TradeCount())  
strOut += "," + str(shortNPV) + ',' + str(shortDelta) + ',' + str(SHORT_CALL.TradeCount())  
strOut += "," + str(netNPV) + ',' + str(netDelta) 

for i in range(len(refDates)-2):
	idx = i+1 
	tDate = refDates[idx]  
	
	BuildHistoricalScenario(tDate,SCEN,CURVES,VOLS,RATES)  

	#GET MARKET DATA 
	futurePrice = SCEN['CURVES'][commodity][contract]['Close']  

	#ANALYZE EXISTING PORTFOLIO TO TRACK P&L AND RISK  
	longNPV = LONG_CALL.NPV(SCEN)  
	shortNPV = SHORT_CALL.NPV(SCEN)
 	netNPV = PORT.NPV(SCEN)  

	LONG_DELTAS = dict()  
	SHORT_DELTAS = dict()  
	PORT_DELTAS = dict()  

	LONG_CALL.Deltas(SCEN,LONG_DELTAS)  
	SHORT_CALL.Deltas(SCEN,SHORT_DELTAS)  
	PORT.Deltas(SCEN,PORT_DELTAS)
	longDelta = LONG_DELTAS[commodity][contract]  
	shortDelta = SHORT_DELTAS[commodity][contract]  
	netDelta = PORT_DELTAS[commodity][contract]  

	#DELTA HEDGE SUBPORTFOLIOS ACCORDING TO PLAN  
	if idx % longHedgeTime == 0:  
		DeltaHedgePortfolio(LONG_CALL,SCEN)  
	if idx % shortHedgeTime == 0:  
		DeltaHedgePortfolio(SHORT_CALL,SCEN) 

	strOut += '\n' + tDate.isoformat() + "," + str(futurePrice) + "," + str(longNPV) + ',' + str(longDelta) + ',' + str(LONG_CALL.TradeCount())  
	strOut += "," + str(shortNPV) + ',' + str(shortDelta) + ',' + str(SHORT_CALL.TradeCount())  
	strOut += "," + str(netNPV) + ',' + str(netDelta)  
 
#ANALYZE AND FLATTEN ON LAST DATE
lastDate = refDates[-1]  
BuildHistoricalScenario(lastDate,SCEN,CURVES,VOLS,RATES)  
futurePrice = SCEN['CURVES'][commodity][contract]['Close']

DeltaHedgePortfolio(LONG_CALL,SCEN)
DeltaHedgePortfolio(SHORT_CALL,SCEN)   
 
#ANALYZE EXISTING PORTFOLIO TO TRACK P&L AND RISK  
longNPV = LONG_CALL.NPV(SCEN)  
shortNPV = SHORT_CALL.NPV(SCEN)
netNPV = PORT.NPV(SCEN)  
LONG_DELTAS = dict()  
SHORT_DELTAS = dict()  
PORT_DELTAS = dict()  
LONG_CALL.Deltas(SCEN,LONG_DELTAS)  
SHORT_CALL.Deltas(SCEN,SHORT_DELTAS)  
PORT.Deltas(SCEN,PORT_DELTAS)
longDelta = LONG_DELTAS[commodity][contract]  
shortDelta = SHORT_DELTAS[commodity][contract]  
netDelta = PORT_DELTAS[commodity][contract]  

strOut += '\n' + lastDate.isoformat() + "," + str(futurePrice) + "," + str(longNPV) + ',' + str(longDelta) + ',' + str(LONG_CALL.TradeCount())  
strOut += ',' + str(shortNPV) + ',' + str(shortDelta) + ',' + str(SHORT_CALL.TradeCount())  
strOut += ',' + str(netNPV) + ',' + str(netDelta) 

outfile = open('testRun001_output.csv','w')  
outfile.write(strOut)  
outfile.close()  

print 'Single simulation completed',str((datetime.now() - timeStart).seconds),'seconds' 
