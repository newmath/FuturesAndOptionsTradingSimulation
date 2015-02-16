#!/opt/local/bin/python
#
# 20131227
# Joshua Zimmerman
# Subroutines for calculating trades required to mitigate delta risks to
# individual futures contracts

from loadFuturesConfig import *
from Future import *

def DeltaHedgePortfolio(PORTFOLIO,SCEN):
    #COMPUTE DELTAS TO INDIVIDUAL CONTRACTS
    DELTAS = dict()
    PORTFOLIO.Deltas(SCEN,DELTAS)
    #FOR EACH DELTA, ADD OFFSETTING FUTURE TRADE TO PORTFOLIO
    #   DELTA HASH ORGANIZED BY COMMODITY AND CONTRACT EXPIRY
    for commodity in DELTAS.keys():
        contractSize = GetContractQuantityByTicker(commodity)
        for expCode in DELTAS[commodity].keys():
            delta = DELTAS[commodity][expCode]
            tradeSize = round(-1 * delta,0)
            if abs(tradeSize) > 0:
                fixedRate = SCEN['CURVES'][commodity][expCode]['Close']
                X = Future(commodity,expCode,fixedRate,tradeSize,contractSize)
                PORTFOLIO.Trades.append(X)
