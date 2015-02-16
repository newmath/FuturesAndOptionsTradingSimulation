class Future:  
	Ticker = ''  
	ExpiryCode = ''  
	Quantity = 0.0    
	FixedRate = 0.0   
	ContractSize = 0.0 

	def __init__(self,ticker,expiryCode,fixedRate,quantity,contractSize):  
		self.Ticker = ticker
		self.ExpiryCode = expiryCode  
		self.Quantity = float(quantity)  
		self.FixedRate = float(fixedRate)  
		self.ContractSize = float(contractSize)  

	def NPV(self,SCENARIO):  
		dblForward = SCENARIO['CURVES'][self.Ticker][self.ExpiryCode]['Close']     
		dblNPV =  float(self.Quantity) * float(self.ContractSize) * (dblForward - self.FixedRate)     
		return round(dblNPV,2)  

	def Deltas(self,SCENARIO,RISK):  
		if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()   
		if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0    
		dblDelta = self.Quantity  
		RISK[self.Ticker][self.ExpiryCode] += dblDelta  

	def Gammas(self,SCENARIO,RISK):  
		if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()   
		if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0    
		dblGamma = 0.0  
		RISK[self.Ticker][self.ExpiryCode] += dblGamma  

	def Vegas(self,SCENARIO,RISK): 
		if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()   
		if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0    
		dblVega = 0.0  
		RISK[self.Ticker][self.ExpiryCode] += dblVega   

	def Thetas(self,SCENARIO,RISK): 
		if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()   
		if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0    
		dblTheta = 0.0  
		RISK[self.Ticker][self.ExpiryCode] += dblTheta
		
	def Rhos(self,SCENARIO,RISK): 
		if not RISK.has_key(self.Ticker): RISK[self.Ticker] = dict()   
		if not RISK[self.Ticker].has_key(self.ExpiryCode): RISK[self.Ticker][self.ExpiryCode] = 0.0    
		dblRho = 0.0  
		RISK[self.Ticker][self.ExpiryCode] += dblRho  
