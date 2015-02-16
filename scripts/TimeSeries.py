
from datetime import date,timedelta 

class TimeSeries: 
        """date-ordered collection of cDataPoint objects
                Attributes:
                        Dates[] - array of datetime.date 
                        Values[] - array of floats   
                        InterpolationMethod - string 
                Allowable Interpolation Methods:
                        FLAT
                        LINEAR
        """
        # DEFAULT LINEAR INTERPOLATION METHOD
        InterpolationMethod = 'FLAT'
        # DEFAULT TO EMPTY DATA ARRAY
        Dates = [] 
        Values = []  
        #
        #       CONSTRUCTORS
        #
        def __init__(self,pDates = [],pValues = []):
                self.Dates = pDates 
                self.Values = pValues 
        #
        #       Add/Update/Delete
        #               Additions and Updates will be handled by same function, Update  
        #
        def Update(self,pDate,pValue):
                #pValue = float(pValue)                  #STANDARDIZE VALUES TO FLOATS   
                if len(self.Dates) == 0:                #TEST EMPTY ARRAY 
                        self.Dates = [pDate]  
                        self.Values = [pValue]  
                elif pDate > self.Dates[len(self.Dates)-1]: #TEST AFTER END   
                        self.Dates.append(pDate) 
                        self.Values.append(pValue) 
                elif pDate < self.Dates[0]:             #TEST BEFORE START 
                        self.Dates.insert(0,pDate) 
                        self.Values.insert(0,pValue) 
                elif pDate == self.Dates[len(self.Dates)-1]: 
                        self.Values[len(self.Dates)-1] = pValue  
                else:                           #ELSE W/IN RANGE OF EXISTING DATA 
                        max = len(self.Dates)-1    
                        min = 0
                        mid = int((min+max)/2)
                        while self.Dates[mid] != pDate and min < (max - 1):  
                                mid = int((min + max)/2)   
                                if pDate > self.Dates[mid]: 
                                        min = mid 
                                else:
                                        max = mid 
                        if self.Dates[mid] == pDate:
                                self.Values[mid] = pValue 
                        else:
                                self.Dates.insert(max,pDate)  
                                self.Values.insert(max,pValue)  

        def GetValueByDate(self,pDate,pInterpolationMethod='FLAT'):  
                if len(self.Dates) == 0: return None
                if pDate >= self.Dates[len(self.Dates)-1]: return self.Values[len(self.Dates)-1] 
                if pDate <= self.Dates[0]: return self.Values[0]        #FLAT EXTRAPOLATION 
                #BINARY SEARCH ON DATES ARRAY TO GET INDEX AND RETURN CORRESPONDING VALUE  
                max = len(self.Dates)-1  
                min = 0
                mid = int((min+max)/2) 
                while self.Dates[mid] != pDate and min < (max - 1):  
                        mid = int((min + max)/2)   
                        if pDate > self.Dates[mid]: 
                                min = mid 
                        else:
                                max = mid 
                if self.Dates[mid] == pDate:
                        return self.Values[mid]  
                else:
                        if pInterpolationMethod == 'LINEAR':
                                #USING DAYS AS UNIT FOR DIVISOR MAY LIMIT THIS TO DAILY TIME SERIES
                                delta = (self.Dates[max] - self.Dates[min])  
                                slope = (self.Values[max] - self.Values[min])/(delta.days * 86400 + delta.seconds)
                                delta_secs = (pDate - self.Dates[min]).days * 86400 + (pDate - self.Dates[min]).seconds  
                                return self.Values[min] + (slope * delta_secs)   
                        else:
                                return self.Values[min]  # USE PRECEDING VALUE FOR ANY MISSING DATA  

        def GetDatesAndValuesByDateRange(self,pDateStart,pDateEnd):  
                #START BY SEARCHING FOR START DATE AND THEN ITERATING THROUGH DATES COLLECTING RETURN VALUES 
                #UNTIL END DATE IS REACHED  
                rDates = []; rValues = []       #INIT RETURN LISTS  
                if len(self.Dates) == 0: return rDates, rValues
                #print 'start',pDateStart,'end',pDateEnd
                if pDateStart > self.Dates[len(self.Dates)-1]: return rDates, rValues
                if pDateStart <= self.Dates[0]:
                        idx = 0
                else:                
                        max = len(self.Dates)-1  
                        min = 0
                        mid = int((min+max)/2) 
                        while self.Dates[mid] != pDateStart and min < (max - 1):  
                                mid = int((min + max)/2)   
                                if pDateStart > self.Dates[mid]: 
                                        min = mid 
                                else:
                                        max = mid 
                        idx = mid
                        if self.Dates[idx] < pDateStart: idx += 1 

                while idx < len(self.Dates) and self.Dates[idx] <= pDateEnd:
                        rDates.append(self.Dates[idx])
                        rValues.append(self.Values[idx])
                        idx += 1
                # RETURN COMPILED LISTS  
                return rDates, rValues

        def FirstDataDate(self):
                if self.Dates == []: return None
                return self.Dates[0]

        def LastDataDate(self):
                if self.Dates == []: return None
                return self.Dates[len(self.Dates)-1]

        def DataCount(self):
                return len(self.Dates)
        
        #
        #       INPUT VALIDATION METHODS
        #
        def IsAllowableInterpolationMethod(pInterpolationMethod):
                _methods = ['FLAT','LINEAR']
                # check passed string against list
                for x in _methods:
                        if pInterpolationMethod == x:
                                return 1
                #OTHERWISE
                return 0
