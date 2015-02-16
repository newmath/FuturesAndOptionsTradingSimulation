#!/opt/local/bin/python

#IMPORT DATE MODULE
from datetime import date, timedelta 
#IMPORT csvdb FOR HANDING ROUTING TABLE FROM FILE
from csvdb import HashTableFromFileAsText
#IMPORT OWN STRING FUNCTION MODULE
from stringFunctions import *

_routing_table = dict()
_opt_exp_dates = dict()
_fut_exp_dates = dict()

def get_routing():
    #VALIDATE EXISTENCE OF HASH TABLE
    global _routing_table
    if len(_routing_table.keys()) > 0:
        return _routing_table
    else:
        _routing_table = HashTableFromFileAsText('../config/commodities_config.csv')
        return _routing_table


def GetFutureTickerByOptionTicker(_ticker = '',_type = '',exchange='NYMEX'):
    #print 'GetFutureTickerByOptionTicker',_ticker,_type
    if _type == 1:
        _criteria = 'CallTicker'
    else:
        _criteria = 'PutTicker'
    _target = 'ExchangeTicker'
    for key in get_routing().keys():
        #print 'routing key', key
        try:
            if get_routing()[key][_criteria] == _ticker and get_routing()[key]['Exchange'] == exchange:
                #print 'option ticker found'
                return get_routing()[key][_target]
        except ValueError:
            pass
    #OTHERWISE RETURN EMPTY STRING
    return ''

def GetTickerByFutureTicker(_value1,_value2):
    _criteria1 = 'ExchangeTicker'
    _criteria2 = 'Exchange'
    _target = 'Ticker'
    for key in get_routing().keys():
        if get_routing()[key][_criteria1] == _value1 and get_routing()[key][_criteria2] == _value2:
            return get_routing()[key][_target]

def GetContractQuantityByTicker(_ticker):
    _criteria = 'Ticker'
    _target = 'ContractQuantity'
    for key in get_routing().keys():
        if get_routing()[key][_criteria] == _ticker:
            #print 'quoteMultiplier',_ticker,get_routing()[key][_target]
            return float(get_routing()[key][_target])
    return 1

def GetQuoteMultiplierByTicker(_ticker):
    _criteria = 'Ticker'
    _target = 'QuoteMultiplier'
    for key in get_routing().keys():
        if get_routing()[key][_criteria] == _ticker:
            #print 'quoteMultiplier',_ticker,get_routing()[key][_target]
            return float(get_routing()[key][_target])
    return 1

def GetStrikeMultiplierByTicker(_ticker):
    _criteria = 'Ticker'
    _target = 'StrikeMultiplier'
    for key in get_routing().keys():
        if get_routing()[key][_criteria] == _ticker:
            #print 'strikeMultiplier',_ticker,get_routing()[key][_target]
            return float(get_routing()[key][_target])
    return 1
        
def fut_exp_dates():
    global _fut_exp_dates
    if len(_fut_exp_dates.keys()) > 0:
        return _fut_exp_dates
    else:
        exp_file = open('../config/exchange_expiry_dates.csv','r')
        linenum = 0
        for line in exp_file:
            linenum += 1
            if linenum == 1: continue
            fields = line.split(',')
            for j in range(len(fields)):
                fields[j] = clean(fields[j])
            _ticker = fields[2]
            _year = int(fields[3])
            _month = int(fields[4])
            
            dateParts = fields[8].split('-')
            if left(fields[9],1) == '#' or len(dateParts) != 3: continue
            _expDate = date(int(dateParts[0]),int(dateParts[1]),int(dateParts[2]))
            #if _expDate < _refDate: continue
            
            if not _fut_exp_dates.has_key(_ticker): _fut_exp_dates[_ticker] = dict()
            if not _fut_exp_dates[_ticker].has_key(_year): _fut_exp_dates[_ticker][_year] = dict()
            _fut_exp_dates[_ticker][_year][_month] = _expDate
        
        return _fut_exp_dates

def opt_exp_dates():
    global _opt_exp_dates
    if len(_opt_exp_dates.keys()) > 0:
        return _opt_exp_dates
    else:
        exp_file = open('../config/exchange_expiry_dates.csv','r')
        linenum = 0
        for line in exp_file:
            linenum += 1
            if linenum == 1: continue
            fields = line.split(',')
            for j in range(len(fields)):
                fields[j] = clean(fields[j])
            _ticker = fields[2]
            _year = int(fields[3])
            _month = int(fields[4])
            #print fields
            dateParts = fields[9].split('-')
            if left(fields[9],1) == '#' or len(dateParts) != 3: continue
            _expDate = date(int(dateParts[0]),int(dateParts[1]),int(dateParts[2]))
            #if _expDate < _refDate: continue
            #if not FUTURES.has_key(contractCode): FUTURES[contractCode] = dict()           
            if not _opt_exp_dates.has_key(_ticker): _opt_exp_dates[_ticker] = dict()
            if not _opt_exp_dates[_ticker].has_key(_year): _opt_exp_dates[_ticker][_year] = dict()
            _opt_exp_dates[_ticker][_year][_month] = _expDate
        #print 'OPT EXP DATE KEYS: ' + ' | '.join(_opt_exp_dates.keys())
        return _opt_exp_dates

def BuildHistoricalScenario(refDate,SCEN,CURVES,VOLS,RATES):
    #print '*building historical scenario for', refDate.isoformat()
    #SCEN = dict()   #RE-INITIALIZE
    SCEN['SCENDATE'] = refDate
    SCEN['CURVES'] = CURVES[refDate]
    SCEN['VOLS'] = VOLS[refDate]
    SCEN['RATES'] = RATES.GetValueByDate(refDate)
    
