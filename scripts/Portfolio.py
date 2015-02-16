
class Portfolio: 
	# define array of items that are the trades in the portfolio
	# run-time interpretation will handle polymorphism for me   
	Trades = []  
	Cash = 0.0  
	Name = ''

	def __init__(self,name=''):  
		self.Name = name  
		self.Trades = []  
		self.Cash = 0.0  

	def Append(self,X):  
		self.Trades.append(X)  

	def TradeCount(self):  
		return len(self.Trades)  

	def NPV(self,SCENARIO): 
		dblTotal = 0.0   
		for trade in self.Trades:  
			dblTotal += trade.NPV(SCENARIO)  
		return dblTotal  

	def Deltas(self,SCENARIO,RISK):  
		for trade in self.Trades:  
			trade.Deltas(SCENARIO,RISK)  

	def Gammas(self,SCENARIO,RISK):  
		for trade in self.Trades:  
			trade.Gammas(SCENARIO,RISK)  
	
	def Vegas(self,SCENARIO,RISK):  
		for trade in self.Trades:  
			trade.Vegas(SCENARIO,RISK) 

	def Rhos(self,SCENARIO,RISK):  
		for trade in self.Trades:  
			trade.Rhos(SCENARIO,RISK)  
 
