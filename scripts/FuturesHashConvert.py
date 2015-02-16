from datetime import date
from TimeSeriesFunctions import GetDatesAndValuesByDateRange

def ConvertFuturesHashToCurvesHash(FUTURES,CURVES,minDate=date(1900,1,1),maxDate=date(2099,12,31)):
    for code in FUTURES.keys():
        for year in FUTURES[code].keys():
            for month in FUTURES[code][year].keys():
                #COLLECT DATES AND VALUES FOR EACH FUTURE TIMESERIES
                (_dates,_values) = GetDatesAndValuesByDateRange(FUTURES[code][year][month],minDate,maxDate)
                #SAVE IN CURVES HASH
                for i in range(len(_dates)):
                    tDate = _dates[i]
                    tVal = _values[i]
                    crvMonth = str(year) + ('00'+str(month))[-2:]

                    if not tDate in CURVES.keys(): CURVES[tDate] = dict()
                    if not code in CURVES[tDate].keys(): CURVES[tDate][code] = dict()
                    if not crvMonth in CURVES[tDate][code].keys(): CURVES[tDate][code][crvMonth] = dict()

                    CURVES[tDate][code][crvMonth] = tVal
                    
def ConvertFuturesHashToCurveSeriesHash(FUTURES,CURVES,minDate=date(1900,1,1),maxDate=date(2099,12,31)):
    for code in FUTURES.keys():
        for year in FUTURES[code].keys():
            for month in FUTURES[code][year].keys():
                #COLLECT DATES AND VALUES FOR EACH FUTURE TIMESERIES  
                (_dates,_values) = GetDatesAndValuesByDateRange(FUTURES[code][year][month],minDate,maxDate)
                #SAVE IN CURVES HASH
                for i in range(len(_dates)):
                    tDate = _dates[i]
                    tVal = _values[i]
                    crvMonth = str(year) + ('00'+str(month))[-2:]

                    if not code in CURVES.keys(): CURVES[code] = dict()
                    if not tDate in CURVES[code].keys(): CURVES[code][tDate] = dict()
                    if not crvMonth in CURVES[code][tDate].keys(): CURVES[code][tDate][crvMonth] = dict()

                    CURVES[code][tDate][crvMonth] = tVal
                    
def PrintAverageCurveVolume(CURVES,contract=''):
    for code in CURVES.keys():
        total = 0.0
        count = 0
        if len(contract) > 0 and contract != code: continue 
        for refdate in CURVES[code].keys():
            count += 1
            for crvmonth in CURVES[code][refdate].keys():
                #print code, refdate, crvmonth
                if type(CURVES[code][refdate][crvmonth]) == type(dict()):
                    total += CURVES[code][refdate][crvmonth]['Volume']
        print code, str(int(round(total / count,0)))
