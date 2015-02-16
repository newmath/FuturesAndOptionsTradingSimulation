#IMPORT SYS FOR HANDLING COMMAND LINE ARGUMENTS
import sys
#IMPORT OS FOR FILE I/O
import os.path
import os 
#IMPORT datetime for using dates to reference data
from datetime import date, timedelta
#IMPORT pickle FOR first pass at database
import pickle


#IMPORT MATH MODULE FOR NATURAL LOG
from math import log
#IMPORT OWN STRING FUNCTION MODULE
from stringFunctions import *
#IMPORT BLACK SCHOLES MODULE
from black_scholes import *
#IMPORT TimeSeries
from TimeSeries import *
from cCurve import *
from loadFuturesConfig import *
  

#CONFIG VARS
futDbFileName = '../db/tsFutures.dat'
optDbFileName = '../db/tsVols.dat'
noptDbFileName = '../db/tsNVols.dat'
dfCurveFileName = '../db/tsDFCurves.dat'  

#PRICE ERROR CODE
ncPRICE_ERROR = -666.666  

#PROCESS REFERENCE DATE FROM ARGS
tDate = date.today()  
if len(sys.argv) > 1:  
	dateString = sys.argv[1]  
else: 
	dateString = str(tDate.year) + right('00'+str(tDate.month),2) + right('00'+str(tDate.day),2)  

refYear = int(dateString[:4])
refMonth = int(dateString[4:6])
refDay = int(dateString[6:8])
refDate = date(refYear,refMonth,refDay)

print 'refDate: ' + refDate.isoformat()

#CREATE LIST OF FILES TO LOOP THROUGH USING RELATIVE PATHS
urlFile = '../config/url_list.txt'
f = open(urlFile,'r')
urlList = f.readlines()
f.close()

file_path = '../settlement_data_files/' + dateString
out_file_path = '/var/www/html/' + dateString

fileList =[]
exchList = [] 
for line in urlList:
    fields = line.strip().split(',')
    url = fields[0]
    file_name = file_path + '/' + url.split('/')[-1]
    fileList.append(file_name)
    exchList.append(fields[1])

def cmeSettlementDataFileRowType(rowString = ''):
    #HANDLE EMPTY CASE
    if rowString == '': return ''
    #IDENTIFY TOTALS ROWS
    if left(rowString,5) == 'TOTAL': return 'TOTAL'
    words = line.split(' ')
    #IDENTIFY FUTURES CONTRACT HEADERS
    if rowString.find('Future') > -1 or rowString.find('FUTURE') > -1:
        return 'FUTURES CONTRACT HEADER'
    #IDENTIFY OPTION HEADER ROW BY LAST WORD BEING 'CALL' OR 'PUT'
    if words[-1] == 'CALL' or words[-1] == 'PUT':
        return 'OPTION CONTRACT HEADER' 
    #IDENTIFY SINGLE OPTION STRIKES
    if words[0].isdigit() or left(words[0],1) == '-':
        return 'OPTION CONTRACT RECORD'
    #IDENTIFY FUTURES CONTRACT RECORDS BY CHECKING FIRST WORD IS CONTRACT MONTH CODE
    if len(words[0])==5 and left(words[0],3).isalpha() and right(words[0],2).isdigit():
        return 'FUTURE CONTRACT RECORD'
    #OTHERWISE A FUTURES CONTRACT HEADER
    return 'FUTURES CONTRACT HEADER'

def cmeIntMonthFromThreeLetterMonth(mmm = ''):
    if mmm == '': return -1
    months = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JLY':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    retVal = months[mmm.upper()]
    if retVal != None:
        return retVal
    else:
        return -1

def convertPriceStringToFloat(strPrice = ''):   
    #VALIDATE EMPTY SETTLES
    if strPrice == '----' or len(strPrice) == 0: return ncPRICE_ERROR    
    #CONVERT PRICE TO FLOAT
    parts = strPrice.split("'")
    fltPrice = float(parts[0])
    if len(parts) > 1:
        fltPrice += float(parts[1])/8.0
    return fltPrice  

#INIT MARKET DATA HASH TABLE
FUTURES = dict()
VOLS = dict()
NVOLS = dict()

dfCurve = cCurve()
dfCurve.SetInterpMethod(1)  #log-linear, for discount factors  
dfCurve.Add(cCurvePoint(refDate,1.0))  

#INIT refDate global to script
fileNum = 0
for file_name in fileList:
    fileNum += 1
    #VALIDATE FILE NAME
    #if not os.path.isfile(fileName):
    #print 'cant find file:', fileName
    #    continue
    #IDENTIFY EXCHANGE FOR THIS FILE
    exchange = exchList[fileNum-1]
    #TEST IF FILE EXISTS, SKIPPING IF NOT
    if not os.path.exists(file_name): continue
    #OPEN FILE FOR READING
    dataFile = open(file_name,'r')
    #GET DATA REFERENCE DATE FROM TOP LINE OF EACH FILE
    line = dataFile.readline().strip(' ')
    words = line.split(' ')
    dateString = words[5]
    dateParts = dateString.split('/')
    #print 'Date String for ' + file_name + ': ' + dateString
    #refDate = date(2000+int(dateParts[2]),int(dateParts[0]),int(dateParts[1]))
    _refDate = refDate
    #print file_name
    #print 'Reference Date: ' + refDate.isoformat()
    #LoadDiscountFactorsFromFile(refDate)
   
    #INIT RUNNING DISCOUNT FACTOR TO 1  
    dblRunningDF = 1.0  

    #SKIP NEXT 2 LINES
    dataFile.readline(); dataFile.readline()

    #INITIALIZE FILE LINE VARIABLES
    lineCount = 3
    contractCode = ''
    contractType = ''
    contractMonth = -1
    contractYear = -1
    contractOptionType = 0
    optionForward = -1
    contractTicker = ''
    rowType = ''
    iTicker = ''
    quoteMultiplier = 1.0
    strikeMultiplier = 1.0
    for line in dataFile:
        lineCount += 1
        #IDENTIFY ROW TYPE
        line = clean(line)
        rowType = cmeSettlementDataFileRowType(line)
        if rowType == '':
            continue
        elif rowType == 'TOTAL':
            continue
        elif rowType == 'FUTURES CONTRACT HEADER':
            contractCode = line.split(' ')[0]
            iTicker = GetTickerByFutureTicker(contractCode,exchange)
            quoteMultiplier = GetQuoteMultiplierByTicker(iTicker)
        elif rowType == 'FUTURE CONTRACT RECORD':
            #ONLY INCLUDE VALID TICKERS
            if iTicker == None: continue
            if quoteMultiplier == None: continue
            #DETERMINE CONTRACT MONTH FROM CODE
            strContractMonth = line.split(' ')[0]
            contractMonth = cmeIntMonthFromThreeLetterMonth(left(strContractMonth,3))
            contractYear = 2000 + int(right(strContractMonth,2))
            #GET SETTLEMENT PRICE
            strSettlePrice = clean(mid(line,46,9))
            strOpenPrice = clean(mid(line,6,9))
            strHighPrice = clean(mid(line,16,9))
            strLowPrice = clean(mid(line,26,9))
            strVolume = clean(mid(line,66,9))
            #CONVERT PRICE STRINGS TO FLOATS
	    fltSettlePrice = convertPriceStringToFloat(strSettlePrice)  
	    if fltSettlePrice == ncPRICE_ERROR: continue  
	    fltOpenPrice = convertPriceStringToFloat(strOpenPrice)  
	    fltHighPrice = convertPriceStringToFloat(strHighPrice)  
	    fltLowPrice = convertPriceStringToFloat(strLowPrice)  
	    fltVolume = convertPriceStringToFloat(strVolume)  
            if fltVolume == ncPRICE_ERROR: fltVolume = 0  
            #SAVE PRICES TO DATATBASE
            if not FUTURES.has_key(iTicker): FUTURES[iTicker] = dict()
            if not FUTURES[iTicker].has_key(contractYear):
                FUTURES[iTicker][contractYear] = dict()
            if not FUTURES[iTicker][contractYear].has_key(contractMonth):
                FUTURES[iTicker][contractYear][contractMonth] = dict()
            FUTURES[iTicker][contractYear][contractMonth]["Close"] = fltSettlePrice * quoteMultiplier
            if fltOpenPrice != ncPRICE_ERROR: FUTURES[iTicker][contractYear][contractMonth]["Open"] = fltOpenPrice * quoteMultiplier
            if fltHighPrice != ncPRICE_ERROR: FUTURES[iTicker][contractYear][contractMonth]["High"] = fltHighPrice * quoteMultiplier  
	    if fltLowPrice != ncPRICE_ERROR: FUTURES[iTicker][contractYear][contractMonth]["Low"] = fltLowPrice * quoteMultiplier
	    FUTURES[iTicker][contractYear][contractMonth]["Volume"] = fltVolume  
	    #BUILD DISCOUNT FACTOR CURVE FROM EURODOLLAR FUTURES (W/O CONVEXITY ADJUSTMENT TO START)  
	    if iTicker == 'ED': 
		#IGNORE NON-CORE FUTURES, USING ONLY H,M,U,Z  
		if contractMonth == 3 or contractMonth == 6 or contractMonth == 9 or contractMonth == 12:    
			dblForwardRate = (100 - fltSettlePrice) / 100  #ABS VAL  

			if dfCurve.length() == 1:  
				dfDate = fut_exp_dates()[iTicker][contractYear][contractMonth]  
				dblTenor = float((dfDate - refDate).days) / 365.0  
				dblDF = (1+ dblForwardRate / 4) ** (-4 * dblTenor)  
				dblRunningDF *= dblDF  
				dfCurve.Add(cCurvePoint(dfDate,dblRunningDF))   
				#print iTicker,contractYear,contractMonth,fltSettlePrice,dblForwardRate,dfCurve.length()    

			dblForwardDF = (1 + dblForwardRate / 4) ** (-1)  
			dblRunningDF *= dblForwardDF  
			if contractMonth + 3 > 12:  
				forwardContractMonth = 3  
				forwardContractYear = contractYear + 1  
			else: 
				forwardContractMonth = contractMonth + 3  
				forwardContractYear = contractYear 
			if not fut_exp_dates()[iTicker].has_key(forwardContractYear):  
				continue   
			dfDate = fut_exp_dates()[iTicker][forwardContractYear][forwardContractMonth]  
			dfCurve.Add(cCurvePoint(dfDate,dblRunningDF))    
			#print iTicker,contractYear,contractMonth,fltSettlePrice,dblForwardRate,dfCurve.length()    
        elif rowType == 'OPTION CONTRACT HEADER':
            words = line.split(' ')
            if words[-1].upper() == 'CALL':
                contractOptionType = 1
            else:
                contractOptionType = -1
            #GET FUTURE TICKER
            optionTicker = words[0]
            contractCode = GetFutureTickerByOptionTicker(optionTicker,contractOptionType,exchange)
            iTicker = GetTickerByFutureTicker(contractCode,exchange)
            quoteMultiplier = GetQuoteMultiplierByTicker(iTicker)
            strikeMultiplier = GetStrikeMultiplierByTicker(iTicker)            
            #GET CONTRACT MONTH
            strContractMonth = words[1]
            contractMonth = cmeIntMonthFromThreeLetterMonth(left(strContractMonth,3))
            if right(strContractMonth,2).isdigit():
                contractYear = 2000 + int(right(strContractMonth,2))
            else:
                contractYear = -1
        elif rowType == 'OPTION CONTRACT RECORD':
            #IGNORE OPTIONS FOR WHICH WE DONT HAVE CONTRACT CODES
            if contractCode == '': continue
            if contractMonth == -1: continue
            if contractYear == -1: continue
            if iTicker == None: continue
            words = line.split(' ')
            #GET STRIKE
            fltStrike = float(words[0]) * strikeMultiplier
            #GET FORWARD PRICE FOR OPTION CONTRACT
	    if not FUTURES[iTicker].has_key(contractYear): continue  
            if FUTURES[iTicker][contractYear].has_key(contractMonth):
                #print contractCode,contractYear,contractMonth,fltStrike
                fltForward = FUTURES[iTicker][contractYear][contractMonth]["Close"]
            else:
                #IGNORE OPTIONS
                continue
            if fltForward <= 0:
                #print 'zero forward',contractCode,contractYear,contractMonth
                continue
            #GET SETTLEMENT PRICE
            strSettlePrice = clean(mid(line,46,9))
            if strSettlePrice.isalpha(): continue
            if strSettlePrice == '----': continue
            parts = strSettlePrice.split("'")
            if len(parts[0]) == 0:
                fltSettlePrice = 0
            else:
                fltSettlePrice = float(parts[0]) * quoteMultiplier
            if len(parts) > 1:
                fltSettlePrice += (float(parts[1])/8.0 * quoteMultiplier)
            #GET EXPIRY DATE AND TENOR
            #print contractCode,iTicker,contractYear,contractMonth
            if not opt_exp_dates().has_key(iTicker): continue
            if not opt_exp_dates()[iTicker].has_key(contractYear): continue                
            if opt_exp_dates()[iTicker][contractYear].has_key(contractMonth):
                expDate = opt_exp_dates()[iTicker][contractYear][contractMonth]
            else:
                 continue   
            tenor = float((expDate - refDate).days)/365.0
            #GET DISCOUNT RATE
            dblDF = dfCurve.GetValueByDate(expDate)
            if tenor == 0:
                dblRate = 0.01
            else:
                dblRate = (float(-1) / tenor) * log(dblDF)
            
            #rate = .01  

            #CALC IMP VOL
            fltSkew = fltStrike / fltForward
            #IGNORE IN-THE-MONEY OPTIONS
            if contractOptionType == 1 and fltSkew < 1: continue
            if contractOptionType == -1 and fltSkew > 1: continue
            #STILL NEEDS TO BE WRITTEN
            sigma = option_implied_vol(fltForward,fltStrike,fltSettlePrice,dblRate,tenor,contractOptionType)
            normal_sigma = option_implied_vol_normal(fltForward,fltStrike,fltSettlePrice,dblRate,tenor,contractOptionType)
            #SAVE IN HASH TABLE
            if not VOLS.has_key(iTicker): VOLS[iTicker] = dict()
            if not VOLS[iTicker].has_key(contractYear): VOLS[iTicker][contractYear] = dict()
            if not VOLS[iTicker][contractYear].has_key(contractMonth):
                VOLS[iTicker][contractYear][contractMonth] = dict()
            if not NVOLS.has_key(iTicker): NVOLS[iTicker] = dict()
            if not NVOLS[iTicker].has_key(contractYear): NVOLS[iTicker][contractYear] = dict()
            if not NVOLS[iTicker][contractYear].has_key(contractMonth):
                NVOLS[iTicker][contractYear][contractMonth] = dict()
            #
            #if contractCode == 'C' and contractYear == 2010 and contractMonth == 12:
            #    print contractCode,contractYear,contractMonth,fltForward,fltStrike,fltSettlePrice,rate,tenor,sigma
            #
            VOLS[iTicker][contractYear][contractMonth][fltSkew] = sigma
            NVOLS[iTicker][contractYear][contractMonth][fltSkew] = normal_sigma
    #CLOSE FILE
    dataFile.close()

#DEFINE SKEWS FOR USE IN VOL SURFACES, USE ONE OR THE OTHER
skews = [.5,.8,.9,.95,1,1.05,1.1,1.2,1.5]
SMILES = dict()
NSMILES = dict()

# COMPUTE AND SAVE DESIRED SKEWS FROM STORED SKEWS
for code in sorted(VOLS.keys()):
    if not SMILES.has_key(code):SMILES[code] = dict()
    if not NSMILES.has_key(code):NSMILES[code] = dict()
    for year in sorted(VOLS[code].keys()):
        if not SMILES[code].has_key(year): SMILES[code][year] = dict()
        if not NSMILES[code].has_key(year): NSMILES[code][year] = dict()
        for month in sorted(VOLS[code][year].keys()):
            _skews = []
            _vols = []
            _nvols = []
            _smile = []
            _nsmile = []
            #BUILD ORDERED SKEW ARRAY
            for skew in sorted(VOLS[code][year][month].keys()):
                _skews.append(skew)
                _vols.append(VOLS[code][year][month][skew])
                _nvols.append(NVOLS[code][year][month][skew])
            #INTERPOLATE TO FIND DESIRED SKEWS
            for i in range(len(skews)):
                v = 0
                nv = 0
                if skews[i] <= _skews[0]:    #FLAT EXTRAPOLATION
                    v = _vols[0]
                    nv = _nvols[0]
                elif skews[i] >= _skews[-1]:
                    v = _vols[-1]
                    nv= _nvols[-1]
                else:
                    j = 1
                    while j < (len(_skews)) and skews[i] >= _skews[j]:
                        j += 1
                    #j -= 1  #STEP BACK ONE
                    v = _vols[j-1] + ((_vols[j] - _vols[j-1])/(_skews[j] - _skews[j-1])) * (skews[i] - _skews[j-1])
                    nv = _nvols[j-1] + ((_nvols[j] - _nvols[j-1])/(_skews[j] - _skews[j-1])) * (skews[i] - _skews[j-1])
                _smile.append(v)
                _nsmile.append(nv)
            #SAVE SMILE TO RESULT HASH
            SMILES[code][year][month] = _smile
            NSMILES[code][year][month] = _nsmile

# CREATE OUTPUT DIRECTORY IF NECESSARY
if not os.path.exists(out_file_path): os.mkdir(out_file_path)

# PRINT FUTURES HASH TABLE TO FILE FOR TEST
output = 'Code,Year,Month'
fields = ['Open','High','Low','Close','Volume']  
for field in fields:  
    output += "," + field  

for code in sorted(FUTURES.keys()): 
    for year in sorted(FUTURES[code].keys()):
        for month in sorted(FUTURES[code][year].keys()):
            output += '\n' + code + ',' + str(year) + ',' + str(month)  
	    for field in fields:  
		output += ','  
		if FUTURES[code][year][month].has_key(field): 
			output += str(FUTURES[code][year][month][field])  

outFile = open(out_file_path + '/' + 'mktdata_futures_'+refDate.isoformat() + '.csv','w')
print >> outFile, output
outFile.close()

#SAVE FUTURES PRICES TO FUTURES PRICE TIME SERIES DB
_FUT = dict()
# LOAD DATABASE FROM FILE IF IT EXISTS
if os.path.isfile(futDbFileName):  
        dbfile = open(futDbFileName) 
        _FUT = pickle.load(dbfile) 
        dbfile.close()
#SAVE PRICES TO HASH TABLE
for code in FUTURES.keys():
    if not _FUT.has_key(code): _FUT[code] = dict()
    for year in FUTURES[code].keys():
        if not _FUT[code].has_key(year): _FUT[code][year] = dict()
        for month in FUTURES[code][year].keys():
            if not _FUT[code][year].has_key(month):
                _FUT[code][year][month] = TimeSeries()
            _FUT[code][year][month].Update(refDate,FUTURES[code][year][month])
#SAVE HASH DB TO FILE
dbfile = open(futDbFileName,'w')
pickle.dump(_FUT,dbfile)
dbfile.close()


#PRINT VOL SURFACE DATA TO FILE FOR TEST
output = 'Code,Year,Month,Future'
for j in range(len(skews)):
    output += ',' + str(skews[j])
#COPY OUTPUT HEADER TO NORMAL VOLS OUTPUT
n_output = output
for code in sorted(SMILES.keys()):
    for year in sorted(SMILES[code].keys()):
        for month in sorted(SMILES[code][year].keys()):
            output += '\n' + code + ',' + str(year) + ',' + str(month)
            n_output += '\n' + code + ',' + str(year) + ',' + str(month)
	    output += ',' + str(FUTURES[code][year][month]['Close'])
	    n_output += ',' + str(FUTURES[code][year][month]['Close']) 
            for vol in SMILES[code][year][month]:
                output += ',' + str(round(vol*100,2))
            for vol in NSMILES[code][year][month]:
                n_output += ',' + str(round(vol*1,2))

outFile = open(out_file_path + '/' + 'mktdata_vols_'+refDate.isoformat() + '.csv','w')
print >> outFile, output
outFile.close()

outFile = open(out_file_path + '/' + 'mktdata_normal_vols_'+refDate.isoformat() + '.csv','w')
print >> outFile, n_output
outFile.close()

#SAVE LOGNORMAL VOLS TO VOL SURFACE TIME SERIES DB
_VOLS = dict()
# LOAD DATABASE FROM FILE IF IT EXISTS
if os.path.isfile(optDbFileName):  
        dbfile = open(optDbFileName) 
        _VOLS = pickle.load(dbfile) 
        dbfile.close()        
#SAVE PRICES TO HASH TABLE
for code in SMILES.keys():
    if not _VOLS.has_key(code): _VOLS[code] = dict()
    for year in SMILES[code].keys():
        if not _VOLS[code].has_key(year): _VOLS[code][year] = dict()
        for month in SMILES[code][year].keys():
            if not _VOLS[code][year].has_key(month):
                _VOLS[code][year][month] = TimeSeries()
            _VOLS[code][year][month].Update(refDate,SMILES[code][year][month])
#SAVE HASH DB TO FILE
dbfile = open(optDbFileName,'w')
pickle.dump(_VOLS,dbfile)
dbfile.close()

#SAVE NORMAL VOLS TO VOL SURFACE TIME SERIES DB
_VOLS = dict()
# LOAD DATABASE FROM FILE IF IT EXISTS
if os.path.isfile(noptDbFileName):  
        dbfile = open(noptDbFileName) 
        _VOLS = pickle.load(dbfile) 
        dbfile.close()        
#SAVE PRICES TO HASH TABLE
for code in NSMILES.keys():
    if not _VOLS.has_key(code): _VOLS[code] = dict()
    for year in NSMILES[code].keys():
        if not _VOLS[code].has_key(year): _VOLS[code][year] = dict()
        for month in NSMILES[code][year].keys():
            if not _VOLS[code][year].has_key(month):
                _VOLS[code][year][month] = TimeSeries()
            _VOLS[code][year][month].Update(refDate,NSMILES[code][year][month])
#SAVE HASH DB TO FILE
dbfile = open(noptDbFileName,'w')
pickle.dump(_VOLS,dbfile)
dbfile.close() 

#UPDATE DF CURVE DB  
dfCurveSeries = TimeSeries()   
if os.path.isfile(dfCurveFileName):  
	dbfile = open(dfCurveFileName,'r')  
	dfCurveSeries = pickle.load(dbfile)  
	dbfile.close() 
dfCurveSeries.Update(refDate,dfCurve)  
dbfile = open(dfCurveFileName,'w')   
pickle.dump(dfCurveSeries,dbfile)  
dbfile.close()   
 
