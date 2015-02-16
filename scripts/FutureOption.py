execfile('black_scholes.py')  
execfile('interpolation.py')  

from math import log

class FutureOption:  
	Ticker = ''  
	ExpiryCode = ''  
	Quantity = 0.0    
	Strike = 0.0   
	ContractSize = 0.0 
	Type = 1 	# 1 for call (default), -1 for put   
	Model = 'lognormal'  
	ExpiryDate = date(1900,1,1)  

	_skews = [0.5,0.8,0.9,0.95,1,1.05,1.1,1.2,1.5]  

	def __init__(self,ticker,futureExpiryCode,expiryDate,strike,type,quantity,contractSize,model='lognormal'):  
		self.Ticker = ticker  
		self.ExpiryCode = futureExpiryCode  
		self.ExpiryDate = expiryDate  
		self.Quantity = quantity  
		self.Strike = strike 
		self.ContractSize = contractSize  
		self.Type = type  
		self.Model = model   

	def ImpliedVol(self,SCENARIO,price):  
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']    
		dblRate = 0.0035  
		dblTenor = (self.ExpiryDate - SCENARIO['SCENDATE']).days / 365.25  
		
		return option_implied_vol(dblForward,self.Strike,price,dblRate,dblTenor,self.Type)  
		
	def NPV(self,SCENARIO):  
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']    
		dblDF = SCENARIO['RATES'].GetValueByDate(self.ExpiryDate)
		dblMoneyness = float(self.Strike) / dblForward  
		dblTenor = float((self.ExpiryDate - SCENARIO['SCENDATE']).days) / float(365)  
  		dblRate = log(dblDF) * (-1 / dblTenor)
  		
		if self.Model == 'lognormal':  
			smile = SCENARIO['VOLS'][self.Ticker][self.ExpiryCode]  
			dblVol = d1Interpolate(dblMoneyness,self._skews,smile)    
			dblOptionPrice = option_price(dblForward,self.Strike,dblVol,dblRate,dblTenor,self.Type)  
		elif self.Model == 'normal': 
			smile = SCENARIO['VOLS'][self.Ticker][self.ExpiryCode]  
			dblVol = d1Interpolate(dblMoneyness,self._skews,smile)    
			dblOptionPrice = option_price_normal(dblForward,self.Strike,dblVol,dblRate,dblTenor,self.Type)  
		else:  
			dblOptionPrice = -1.0  

		dblNPV = dblOptionPrice * float(self.Quantity) * float(self.ContractSize)
		#print dblForward,self.Strike,dblTenor,dblMoneyness,dblVol,dblRate
 		return round(dblNPV,2)  
 
        def Deltas(self,SCENARIO,RISK):
                if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()
                if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0
                #COLLECT MARKET DATA REQUIRED FOR ALL OPTION MODELS
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']    
		dblDF = SCENARIO['RATES'].GetValueByDate(self.ExpiryDate)
		dblMoneyness = float(self.Strike) / dblForward  
		dblTenor = float((self.ExpiryDate - SCENARIO['SCENDATE']).days) / float(365)  
  		dblRate = log(dblDF) * (-1 / dblTenor)
  		#CALCULATE DELTAS DEPENDING ON MODEL
                if self.Model == 'lognormal':  
			smile = SCENARIO['VOLS'][self.Ticker][self.ExpiryCode]  
			dblVol = d1Interpolate(dblMoneyness,self._skews,smile)    
			dblDelta = black_delta(dblForward,self.Strike,dblVol,dblRate,dblTenor,self.Type)  
		elif self.Model == 'normal': 
			dblDelta = 0.0  
		else:  
			dblDelta = 0.0
  		#ADD DELTA TO HASH
		RISK[self.Ticker][self.ExpiryCode] += dblDelta * self.Quantity

	def Gammas(self,SCENARIO,RISK):
                if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()
                if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0
                #COLLECT MARKET DATA REQUIRED FOR ALL OPTION MODELS
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']    
		dblDF = SCENARIO['RATES'].GetValueByDate(self.ExpiryDate)
		dblMoneyness = float(self.Strike) / dblForward  
		dblTenor = float((self.ExpiryDate - SCENARIO['SCENDATE']).days) / float(365) 
  		dblRate = log(dblDF) * (-1 / dblTenor)
  		#CALCULATE RISK DEPENDING ON MODEL
                if self.Model == 'lognormal':  
			smile = SCENARIO['VOLS'][self.Ticker][self.ExpiryCode]  
			dblVol = d1Interpolate(dblMoneyness,_skews,smile)    
			dblGamma = black_gamma(dblForward,self.Strike,dblVol,dblRate,dblTenor,self.Type)  
		elif self.Model == 'normal': 
			dblGamma = 0.0  
		else:  
			dblGamma = -1.0  
  		#ADD RISK TO HASH
		RISK[self.Ticker][self.ExpiryCode] += dblGamma * self.Quantity
		
	def Vegas(self,SCENARIO,RISK):
                if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()
                if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0
                #COLLECT MARKET DATA REQUIRED FOR ALL OPTION MODELS
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']    
		dblDF = SCENARIO['RATES'].GetValueByDate(self.ExpiryDate)
		dblMoneyness = float(self.Strike) / dblForward  
		dblTenor = float((self.ExpiryDate - SCENARIO['SCENDATE']).days) / float(365) 
  		dblRate = log(dblDF) * (-1 / dblTenor)
  		#CALCULATE RISK DEPENDING ON MODEL
                if self.Model == 'lognormal':  
			smile = SCENARIO['VOLS'][self.Ticker][self.ExpiryCode]  
			dblVol = d1Interpolate(dblMoneyness,_skews,smile)    
			dblVega = black_vega(dblForward,self.Strike,dblVol,dblRate,dblTenor,self.Type)  
		elif self.Model == 'normal': 
			dblVega = 0.0  
		else:  
			dblVega = -1.0  
  		#ADD RISK TO HASH
		RISK[self.Ticker][self.ExpiryCode] += dblVega * self.Quantity * self.ContractSize      
		
	def Thetas(self,SCENARIO,RISK):
                if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()
                if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0
                #COLLECT MARKET DATA REQUIRED FOR ALL OPTION MODELS
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']    
		dblDF = SCENARIO['RATES'].GetValueByDate(self.ExpiryDate)
		dblMoneyness = float(self.Strike) / dblForward  
		dblTenor = float((self.ExpiryDate - SCENARIO['SCENDATE']).days) / float(365) 
  		dblRate = log(dblDF) * (-1 / dblTenor)
  		#CALCULATE RISK DEPENDING ON MODEL
                if self.Model == 'lognormal':  
			smile = SCENARIO['VOLS'][self.Ticker][self.ExpiryCode]  
			dblVol = d1Interpolate(dblMoneyness,_skews,smile)    
			dblTheta = black_theta(dblForward,self.Strike,dblVol,dblRate,dblTenor,self.Type)  
		elif self.Model == 'normal': 
			dblTheta = 0.0  
		else:  
			dblTheta = -1.0  
  		#ADD RISK TO HASH
		RISK[self.Ticker][self.ExpiryCode] += dblTheta * self.Quantity * self.ContractSize
		
	def Rhos(self,SCENARIO,RISK):
                if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()
                if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0
                #COLLECT MARKET DATA REQUIRED FOR ALL OPTION MODELS
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']    
		dblDF = SCENARIO['RATES'].GetValueByDate(self.ExpiryDate)
		dblMoneyness = float(self.Strike) / dblForward  
		dblTenor = float((self.ExpiryDate - SCENARIO['SCENDATE']).days) / float(365) 
  		dblRate = log(dblDF) * (-1 / dblTenor)
  		#CALCULATE RISK DEPENDING ON MODEL
                if self.Model == 'lognormal':  
			smile = SCENARIO['VOLS'][self.Ticker][self.ExpiryCode]  
			dblVol = d1Interpolate(dblMoneyness,_skews,smile)    
			dblRho = black_rho(dblForward,self.Strike,dblVol,dblRate,dblTenor,self.Type)  
		elif self.Model == 'normal': 
			dblRho = 0.0  
		else:  
			dblRho = -1.0  
  		#ADD RISK TO HASH
		RISK[self.Ticker][self.ExpiryCode] += dblRho * self.Quantity * self.ContractSize   
