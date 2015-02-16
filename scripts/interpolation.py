def d1Interpolate(x,X,Y,method='linear'):  
	if method == 'linear': 
		# EXTRAPOLATE FLAT   
		if x <= X[0]:  
			return Y[0]  
		if x >= X[-1]:  
			return Y[-1]  
		# OTHERWISE LOOP THROUGH EACH ITEM  
		for i in range(len(X)-1):  
			if x <= X[i+1]:  
				slope = (Y[i+1] - Y[i]) / (X[i+1] - X[i]) 
				return Y[i] + slope * (x - X[i])   
	else: 
		return -1.0  

