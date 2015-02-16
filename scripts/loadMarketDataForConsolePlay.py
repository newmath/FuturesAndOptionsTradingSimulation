import pickle  
import os  
import sys
sys.path.insert(0,os.getcwd())
from datetime import date
from FuturesHashConvert import *  

startDate = date(2013,8,30)
endDate = date(2099,12,31)  

futFile = '../db/tsFutures.dat'  
volFile = '../db/tsVols.dat'  
rateFile = '../db/tsDFCurves.dat'  

dbfile = open(futFile,'r')  
FUTURESERIES = pickle.load(dbfile)  
dbfile.close()  

dbfile = open(volFile,'r')  
VOLSERIES = pickle.load(dbfile)  
dbfile.close()  

dbfile = open(rateFile,'r')  
DFS = pickle.load(dbfile)  
dbfile.close()  

print 'Futures, Vols, and Rates loaded'  

CURVES = dict()  
ConvertFuturesHashToCurvesHash(FUTURESERIES,CURVES,startDate,endDate)  
VOLS = dict()
ConvertFuturesHashToCurvesHash(VOLSERIES,VOLS,startDate,endDate)  

print 'Market data converted into scenarios'  


