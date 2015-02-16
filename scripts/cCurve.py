from datetime import date, timedelta   
import math  

class cCurvePoint: 
	_default_date = date(1900,1,1)  
	_default_value = 0  

	def __init__(self,curveDate,pointValue): 
		self.Date = curveDate 
		self.Value = pointValue  

	#DEFINE COMPARISON OPERATORS FOR SORTING
	def __eq__(self,point2):  
		return point2.Date == self.Date 

	def __gt__(self,point2):  
		return self.Date > point2.Date 

	def __lt__(self,point2):  
		return self.Date < point2.Date  
	
	def __ge__(self,point2):  
		return self.Date >= point2.Date  

	def __le__(self,point2):  
		return self.Date <= point2.Date  

class cCurve:  
	#DEFINE INTERPOLATION METHODS, DEFAULT TO LINEAR  
	_interp_method = 0  
	_interp_methods = ['linear','log-linear','flat-forward']  
 
	def __init__(self):  
		self._interp_method = 0 
		#DEFINE ARRAY TO STORE OBJECTS OF TYPE cCurvePoint
		self._curve_points = []  

	def SetInterpMethod(self,methodIndex):  
		self._interp_method = methodIndex  

	def length(self):  
		return len(self._curve_points)  
	
	def Add(self,point):  
		self._curve_points.append(point)  
		#SORT LIST IF NECESSARY   
		if len(self._curve_points) > 1: 
			if point <= self._curve_points[-2]:  
				self._curve_points.sort() 

	def Point(self,index):  
		return self._curve_points[index]  
	
	def GetValueByDate(self,refDate):  
		if len(self._curve_points) == 0:
			return 0  
 
		#EXTRAPOLATE FLAT  
		if refDate <= self._curve_points[0].Date: 
			return self._curve_points[0].Value   
		if refDate >= self._curve_points[-1].Date:  
			return self._curve_points[-1].Value  

		#INTERPOLATE USING SET METHOD  
		for i in range(len(self._curve_points)-1):  
			if refDate < self._curve_points[i+1].Date:  
				if self._interp_method == 0:  
					slope = float((self._curve_points[i+1].Value - self._curve_points[i].Value)) / (self._curve_points[i+1].Date - self._curve_points[i].Date).days  
					return self._curve_points[i].Value + slope * (refDate - self._curve_points[i].Date).days   
				if self._interp_method == 1:  
					log_slope = math.log(self._curve_points[i+1].Value / self._curve_points[i].Value) / (self._curve_points[i+1].Date - self._curve_points[i].Date).days  
					log_val = math.log(self._curve_points[i].Value) + log_slope * (refDate - self._curve_points[i].Date).days  
					return math.exp(log_val)   	  
				if self._interp_method == 2:  
					return self.curve_points[i].Value   
				#OTHERWISE, RETURN DEFAULT VALUE  
				return 0     
