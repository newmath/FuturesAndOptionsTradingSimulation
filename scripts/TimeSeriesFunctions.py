from datetime import date

def GetAverageValueByDateRange(TS,pValueField='',pDateStart=date(1900,1,1),pDateEnd=date(3000,12,31)):
        total = 0.0
        count = 0
        if len(TS.Dates) == 0: return 0.0
        if pDateStart > TS.Dates[len(TS.Dates)-1]: return 0.0
        if pDateStart <= TS.Dates[0]:
                idx = 0
        else:                
                max = len(TS.Dates)-1  
                min = 0
                mid = int((min+max)/2) 
                while TS.Dates[mid] != pDateStart and min < (max - 1):  
                        mid = int((min + max)/2)   
                        if pDateStart > TS.Dates[mid]: 
                                min = mid 
                        else:
                                max = mid 
                idx = mid
                
        while idx < len(TS.Dates) and TS.Dates[idx] <= pDateEnd:
                if type(TS.Values[idx]) == type(dict()):
                        total += TS.Values[idx][pValueField]  
                else:
                        total += TS.Values[idx]       
                count += 1
                idx += 1

        if count > 0:
                return total / count
        else:
                return 0.0

def GetDatesAndValuesByDateRange(series,pDateStart,pDateEnd):  
        #START BY SEARCHING FOR START DATE AND THEN ITERATING THROUGH DATES COLLECTING RETURN VALUES 
        #UNTIL END DATE IS REACHED  
        rDates = []; rValues = []       #INIT RETURN LISTS  
        if len(series.Dates) == 0: return rDates, rValues
        #print 'start',pDateStart,'end',pDateEnd
        if pDateStart > series.Dates[len(series.Dates)-1]: return rDates, rValues
        if pDateStart <= series.Dates[0]:
                idx = 0
        else:                
                max = len(series.Dates)-1  
                min = 0
                mid = int((min+max)/2) 
                while series.Dates[mid] != pDateStart and min < (max - 1):  
                        mid = int((min + max)/2)   
                        if pDateStart > series.Dates[mid]: 
                                min = mid 
                        else:
                                max = mid 
                idx = mid
                if series.Dates[idx] < pDateStart: idx += 1 

        while idx < len(series.Dates) and series.Dates[idx] <= pDateEnd:
                rDates.append(series.Dates[idx])
                rValues.append(series.Values[idx])
                idx += 1
        # RETURN COMPILED LISTS  
        return rDates, rValues

