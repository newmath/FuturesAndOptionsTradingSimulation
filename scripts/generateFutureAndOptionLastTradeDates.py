import sys  
from datetime import date, timedelta  
import calendar  

config_file = '../config/commodities_config.csv'  
holiday_file = '../config/cme_holidays.csv'  

HOLIDAYS = dict() 
def LoadHolidaysFromFile():  
	f = open(holiday_file,'r')  
	lines = f.readlines()  
	f.close()
	for line in lines:  
		fields = line.split(',')  
		calendar = fields[0] 
		if not calendar == 'USNY': 
			continue  
		dateString = fields[2]  
		parts = dateString.split('/')  
		if len(parts) < 3: 
			continue 
		year = int(parts[2])  
		month = int(parts[0])  
		day = int(parts[1])  
		HOLIDAYS[date(year,month,day)] = 1  

def IsBusinessDate(pDate): 
	#LOAD HOLIDAYS IF NOT ALREADY DONE 
	if len(HOLIDAYS.keys()) == 0:
		LoadHolidaysFromFile()
 
	#EXCLUDE WEEKENDS AND HOLIDAYS  	
	if pDate.weekday() == 5 or pDate.weekday() == 6:
		return 0 
	if pDate in HOLIDAYS: 
		return 0  
	#OTHERWISE
	return 1 

def AddBusinessDays(pDate,n):  
	if n == 0: 
		return pDate  
	bus_shifts = 1 
	tDate = pDate   
	while bus_shifts <= abs(n):  
		if n > 0:  
			tDate = tDate + timedelta(days=1)  
		else:  
			tDate = tDate + timedelta(days=-1)  

		if IsBusinessDate(tDate):  
			bus_shifts += 1	
	return tDate 

def BusinessDateOnOrBefore(pDate):  
	if IsBusinessDate(pDate): 
		return pDate  
	tDate = AddBusinessDays(pDate,-1)  
	while not IsBusinessDate(tDate):  
		tDate = AddBusinessDays(tDate,-1)  
	return tDate 

def BusinessDateOnOrAfter(pDate):  
	if IsBusinessDate(pDate): 
		return pDate  
	tDate = AddBusinessDays(pDate,1)  
	while not IsBusinessDate(tDate): 
		tDate = AddBusinessDays(tDate,1)  
	return tDate  

def AddMonths(sourcedate,months):
	month = sourcedate.month - 1 + months  
	year = sourcedate.year + month / 12  
	month = month % 12 + 1  
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])  
	return date(year,month,day)  

def DetermineFutureAndOptionExpiry(ticker, year, month): 
	result = []	#DEFINE OUTPUT AS LIST WITH 2 ITEMS, THE FUTURE AND THE OPTION LAST TRADE DATES  

	if ticker == 'CL':
		tDate = AddMonths(date(year,month,25),-1)    
		fut_exp_date = AddBusinessDays(BusinessDateOnOrBefore(tDate),-3)   
		result.append(fut_exp_date)   
		opt_exp_date = AddBusinessDays(fut_exp_date,-3) 
		result.append(opt_exp_date)   
	elif ticker == 'HO' or ticker == 'RB':  
		fut_exp_date = AddBusinessDays(date(year,month,1),-1)  	
		result.append(fut_exp_date)   
		opt_exp_date = AddBusinessDays(fut_exp_date,-3)  	
		result.append(opt_exp_date)   
	elif ticker == 'C' or ticker == 'S' or ticker == 'W' or ticker == 'MW' or ticker == 'KW' or ticker == 'BO' or ticker == 'SM':  
		# COMPUTE FUT EXP DATE AS LAST BIZ DATE BEFORE 15TH OF CAL MONTH
		tDate = AddBusinessDays(date(year,month,15),-1)
		result.append(tDate)  
 		# COMPUTE OPT EXP DATE AS LAST FRI AT LEAST 2 BIZ DATES BEFORE LAST BIZ DATE OF PRIOR CAL MONTH  
		tDate = date(year,month,1)  
		tDate = AddBusinessDays(tDate,-3) 
		while not tDate.weekday() == 4:
			tDate = tDate + timedelta(days=-1)  
		if not IsBusinessDate(tDate):
			tDate = AddBusinessDays(tDate,-1)  
		result.append(tDate)  
	elif ticker == 'DOED': 
		#LAST MONDAY OF CALENDAR MONTH  
		tDate = date(year,month,calendar.monthrange(year,month)[1]) 
		while tDate.weekday() != 0:  
			tDate = tDate + timedelta(days=-1)    
		result.append(tDate)  
		result.append(tDate)  		
	elif ticker == 'LH':  
		tDate = BusinessDateOnOrAfter(date(year,month,1)) 
		fut_exp_date = AddBusinessDays(tDate,9)  
		result.append(fut_exp_date)  
		opt_exp_date = fut_exp_date  
		result.append(opt_exp_date) 
	elif ticker == 'ED': 
		#THIRD WEDS MINUS 2 BUS DAYS  
		tDate = date(year,month,1)  
		wedCount = 0  
		while wedCount < 3:  
			if tDate.weekday() == 2:  
				wedCount += 1 
			tDate = tDate + timedelta(days=1) 
		tDate = tDate + timedelta(days=-1)   
		fut_exp_date = AddBusinessDays(tDate,-2)   
		result.append(fut_exp_date)  
		result.append(fut_exp_date)   
	elif ticker == 'GC' or ticker == 'SI' or ticker == 'HG':  
		#FUT EXP THIRD TO LAST BIZ DATE  
		if month == 12:  
			tDate = date(year+1,1,1)  
		else:  
			tDate = date(year,month+1,1)  
		fut_exp_date = AddBusinessDays(tDate,-3)  
		result.append(fut_exp_date)  
		#OPT EXP 4TH TO LAST BIZ DATE OF PRIOR MONTH  
		tDate = date(year,month,1)  
		opt_exp_date = AddBusinessDays(tDate,-4)   
		if not IsBusinessDate(opt_exp_date + timedelta(days=1)):  
			opt_exp_date = AddBusinessDays(opt_exp_date,-1)  
		result.append(opt_exp_date)  		
	elif ticker == 'PL':  
		#FUT EXP THIRD TO LAST BIZ DATE  
		if month == 12:  
			tDate = date(year+1,1,1)  
		else:  
			tDate = date(year,month+1,1)  
		fut_exp_date = AddBusinessDays(tDate,-3)  
		result.append(fut_exp_date)  
		# OPT EXP THIRD WED OF PREV MONTH 	
		if month == 1:  
			tDate = date(year-1,12,1)  
		else:  
			tDate = date(year,month-1,1)  
		wedCount = 0  
		while wedCount < 3:  
			if tDate.weekday() == 2:  
				wedCount += 1
			tDate = tDate + timedelta(days=1) 
		opt_exp_date = tDate + timedelta(days=-1)   
		if not IsBusinessDate(opt_exp_date + timedelta(days=1)):  
			opt_exp_date = AddBusinessDays(opt_exp_date,-1)  
		result.append(opt_exp_date)  
	elif ticker == 'ES':  
		#THIRD FRIDAY  
		tDate = date(year,month,1)   
		friCount = 0  
		while friCount < 3:  
			if tDate.weekday() == 4:  
				friCount += 1  
			tDate = tDate + timedelta(days=1)  
		fut_exp_date = tDate + timedelta(days=-1)  
		opt_exp_date = fut_exp_date  
		result.append(fut_exp_date)  
		result.append(opt_exp_date)  
	else:
		result = result  
	return result  

def FutureContractCode(month,year):  
	months = {1:'F',2:'G',3:'H',4:'J',5:'K',6:'M',7:'N',8:'Q',9:'U',10:'V',11:'X',12:'Z'}  
	yr = str(year)[2:4]   
	return months[month] + yr  

#READ COMMAND LINE ARGS, DATES IN YYYYMMDD FORMAT    
_config_file = sys.argv[1]  
_output_file = sys.argv[2]  
_start_date = sys.argv[3]  
_end_date = sys.argv[4]  

# PARSE START AND END DATES  
year = int(_start_date[:4])  
month = int(_start_date[4:6])  
day = 1  
startDate = date(year,month,day)  
year = int(_end_date[:4])  
month = int(_end_date[4:6])  
endDate = date(year,month,day)  

#READ TICKER LIST FROM CONFIG FILE  
f = open(_config_file, 'r')  
lines = f.readlines()  
f.close()  
tickers = [] 
exchanges = []   
for line in lines: 
	fields = line.strip().split(',')  
	ticker = fields[1] 
	if ticker == 'Ticker':
		continue  
	tickers.append(ticker)  
	exchange = fields[2]  
	exchanges.append(exchange)  

#START BUILDING OUTPUT FILE 
id = 1  
f = open(_output_file,'w')  
 
f.write('ID,Exchange,Commodity,Year,Month,Contract,FutureTicker,OptionTicker,FutureExpiry,OptionExpiry')    

# FOR EACH TICKER, LOOP THROUGH DATE RANGE  
for i in range(len(tickers)):  
	ticker = tickers[i] 
	exchange = exchanges[i]  
	print ticker + '\t' + exchange

	tDate = startDate  
	while tDate <= endDate:  
		tYear = tDate.year 
		tMonth = tDate.month   
		#print tDate.isoformat()  
		
		tDate = AddMonths(tDate,1)  

		result = DetermineFutureAndOptionExpiry(ticker,tYear,tMonth)   		
		if len(result) < 2: 
			continue   
	
		fut_exp_date = result[0] 
		opt_exp_date = result[1] 	

		output = '\n'+ str(id) + ',' + exchange + ',' + ticker + ','  
		output += str(tYear) + ',' + str(tMonth) + ',' + FutureContractCode(tMonth,tYear) + ',,,'  
		output += fut_exp_date.isoformat() + ',' + opt_exp_date.isoformat()  
		f.write(output) 
		id += 1   
f.close()  
 
