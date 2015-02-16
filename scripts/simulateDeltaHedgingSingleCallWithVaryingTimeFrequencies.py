#!/opt/local/bin/python  
#
# Test run for option-derived futures trading strategy 

#STANDARD PYTHON MODULES
from datetime import datetime, time, date
timeStart = datetime.now()  

#CUSTOM MODULES
from loadFuturesConfig import * 
from Portfolio import * 
from Future import *
from FutureOption import *  
from FuturesHashConvert import * 
from interpolation import *
from deltaHedgePortfolio import *
      
#DEFINE TARGET COMMODITY, REFERENCE FUTURE OPTION AND STRATEGY PARAMETERS 

def SimulateDeltaHedgingCallOptionWithVaryingTimeFrequencies(commodity,contract,moneyness,strike_round,quantity,longHedgeTime,shortHedgeTime,startDate,endDate,targetPnl,stopLoss,CURVES,VOLS,RATES,optionModel='lognormal'):
        contract_size = GetContractQuantityByTicker(commodity)
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
        strike = float(round(forward * moneyness / strike_round,0)) * strike_round    

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

        i = 0
        while i < len(refDates)-1 and netNPV < targetNPV and netNPV > stopLoss:
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

                #INCREMENT INDEX
                i += 1
                
        #FLATTEN POSITIONS, USING LAST DATE IF HAVEN'T PASSED EITHER EARLY EXIT THRESHOLD
        if i < len(refDates)-1:
                i += 1
                #ANALYZE AND FLATTEN ON LAST DATE
                lastDate = refDates[i]  
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

        return netNPV 
