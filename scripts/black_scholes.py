#IMPORT log and sqrt FROM math MODULE
from math import log, sqrt, exp, pi
#IMPORT date AND timedelta FOR HANDLING EXPIRY TIMES
from datetime import date, timedelta

def asian_vol_factor(valDate,startDate,endDate):
    #VALIDATE START DATE RELATIVE TO END DATE AND RETURN NO IMPACT IF ODD
    if startDate > endDate: return 1
    T = (endDate - valDate).days()
    L = (endDate - startDate).days()
    if days_to_expiry > avg_period_length:
        return sqrt(((T - L + 1) * L ** 2 + L * (L - 1) * (2 * L - 1) / 6) / (L ** 2 * T))
    else:
        return sqrt((T + 1) * (2*T + 1) / (6 * L ** 2))

def F(z):
    return (1/sqrt(2*pi)) * exp(-(z ** 2) / 2)

#COPIED APPROX FOR NORMAL CDF TO REPLACE SCIPY, WHICH WAS TOO HARD TO INSTALL AT WORK
# TAKEN FROM http://stackoverflow.com/questions/809362/cumulative-normal-distribution-in-python
def erfcc(x):
    """Complementary error function."""
    z = abs(x)
    t = 1. / (1. + 0.5*z)
    r = t * exp(-z*z-1.26551223+t*(1.00002368+t*(.37409196+
    	t*(.09678418+t*(-.18628806+t*(.27886807+
    	t*(-1.13520398+t*(1.48851587+t*(-.82215223+
    	t*.17087277)))))))))
    if (x >= 0.):
    	return r
    else:
    	return 2. - r

def normalcdf(x):
    return 1. - 0.5*erfcc(x/(2**0.5))

#COPIED FROM GRAEME WEST AND TRANSLATED TO PYTHON
#https://lyle.smu.edu/~aleskovs/emis/sqc2/accuratecumnorm.pdf
def normalcdf_gw(x):
    XAbs = abs(x)
    if XAbs > 37:
        result = 0
    else:
        Exponential = exp(-1.0 * (XAbs ** 2) / 2.0)
        if XAbs < 7.07106781186547:
            Build = 3.52624965998911E-02 * XAbs + 0.700383064443688
            Build = Build * XAbs + 6.37396220353165
            Build = Build * XAbs + 33.912866078383
            Build = Build * XAbs + 112.079291497871
            Build = Build * XAbs + 221.213596169931
            Build = Build * XAbs + 220.206867912376
            result = Exponential * Build
            Build = 8.83883476483184E-02 * XAbs + 1.75566716318264
            Build = Build * XAbs + 16.064177579207
            Build = Build * XAbs + 86.7807322029461
            Build = Build * XAbs + 296.564248779674
            Build = Build * XAbs + 637.333633378831
            Build = Build * XAbs + 793.826512519948
            Build = Build * XAbs + 440.413735824752
            result = result / Build
        else:
            Build = XAbs + 0.65
            Build = XAbs + 4 / Build
            Build = XAbs + 3 / Build
            Build = XAbs + 2 / Build
            Build = XAbs + 1 / Build
            result = Exponential / Build / 2.506628274631

    if x > 0: result = 1 - result
    return result

def option_price(forward,strike,vol,rate,tenor,sign):
    if vol == 0:
        print 'zero vol error'
        return -1
    if strike == 0:  
	print 'zero strike error'
	return -1  
    #sign = +1 for calls and -1 for puts
    if tenor == 0:  
	return sign * (forward - strike)  
    #OTHERWISE   
    d1 = (log(forward/strike) + (.5 * (vol ** 2) * tenor)) / (vol * sqrt(tenor))
    d2 = d1 - vol * sqrt(tenor)
    return exp(-1 * rate * tenor) * (sign * forward * normalcdf_gw(sign * d1) - strike * sign * normalcdf_gw(sign * d2))

def black_delta(forward,strike,vol,rate,tenor,sign):
    if vol == 0:
        if type == 1:
            if forward >= strike:
                return 1
            else:
                return 0
        else:  
            if forward <= strike:
                return -1
            else:
                return 0
    d1 = (log(forward/strike) + (.5 * (vol ** 2) * tenor)) / (vol * sqrt(tenor))
    forwardCallDelta = normalcdf_gw(d1)
    if type == 1:
        return exp(-1*rate*tenor) * forwardCallDelta
    else:
        return exp(-1*rate*tenor) * (forwardCallDelta - 1)

def black_gamma(forward,strike,vol,rate,tenor,sign):
    if vol == 0: return 0
    d1 = (log(forward/strike) + (.5 * (vol ** 2) * tenor)) / (vol * sqrt(tenor))
    return F(d1) / (forward * vol * sqrt(tenor))

def black_vega(forward,strike,vol,rate,tenor,sign):
    d1 = (log(forward/strike) + (.5 * (vol ** 2) * tenor)) / (vol * sqrt(tenor))
    vega = forward * sqrt(tenor) * F(d1) * exp(-1 * rate * tenor) * .01
    return vega

def black_theta(forward,strike,vol,rate,tenor,sign):
    d1 = (log(forward/strike) + (.5 * (vol ** 2) * tenor)) / (vol * sqrt(tenor))
    d2 = d1 - vol * sqrt(tenor)
    theta = forward * F(d1) * vol * exp(-1*rate*tenor) / sqrt(tenor) / float(-2)
    theta += sign * rate * forward * normalcdf_gw(sign * d1) * exp(-1 * rate * tenor)
    theta -= sign * rate * strike * normalcdf_gw(sign * d2)
    theta /= 365
    return theta

def black_rho(forward,strike,vol,rate,tenor,sign):
    d1 = (log(forward/strike) + (.5 * (vol ** 2) * tenor)) / (vol * sqrt(tenor))
    d2 = d1 - vol * sqrt(tenor)
    rho = sign * strike * tenor * exp(-1 * rate * tenor) * normalcdf_gw(sign * d2) * .0001
    return rho

def option_implied_vol(forward,strike,price,rate,tenor,sign):
    #print 'imp vol calc:',forward,strike,price,rate,tenor,sign
    price_err_limit = price/10000
    iteration_limit = 20
    vmax = 1.0  #START SEARCH FOR UPPER VOL BOUND AT 100%
    tprice = 0.0
    while option_price(forward,strike,vmax,rate,tenor,sign) < price:
        vmax += 1
        if vmax > iteration_limit: return -1 #ERROR CONDITION
    vmin = vmax - 1
    vmid = (vmin + vmax)/2
    tprice = option_price(forward,strike,vmid,rate,tenor,sign)
    count = 1
    while abs(tprice - price) > price_err_limit:
        if tprice > price:
            vmax = vmid
        else:
            vmin = vmid
        vmid = (vmin + vmax)/2
        count = count + 1
        if count > iteration_limit:
            print 'option_implied_vol: search iter limit reached'
            print forward,strike,price,rate,tenor,sign
            return vmid #EXIT CONDITION
        tprice = option_price(forward,strike,vmid,rate,tenor,sign)
    return vmid

def option_price_normal(forward,strike,vol,rate,tenor,sign):
    if vol == 0:
        return -1
    #sign = +1 for calls and -1 for puts 
    if tenor == 0:  
	return sign * (forward - strike)   
    d1 = (forward - strike) / (vol * sqrt(tenor))
    return exp(-1 * rate * tenor) * (sign * (forward - strike) * normalcdf_gw(sign * d1) + vol * sqrt(tenor) * F(d1))

def option_implied_vol_normal(forward,strike,price,rate,tenor,sign):
    price_err_limit = price/10000
    iteration_limit = 25  
    vmax = forward    
    tprice = 0.0
    count = 0  
    while option_price_normal(forward,strike,vmax,rate,tenor,sign) < price:
        vmax += forward   
	count += 1  
        if count > iteration_limit: return -1 #ERROR CONDITION
    vmin = vmax - forward   
    vmid = (vmin + vmax)/2
    tprice = option_price_normal(forward,strike,vmid,rate,tenor,sign)
    count = 1
    while abs(tprice - price) > price_err_limit:
        if tprice > price:
            vmax = vmid
        else:
            vmin = vmid
        vmid = (vmin + vmax)/2
        count += 1
        if count > iteration_limit:
            print 'option_implied_vol_normal: search iter limit reached'
            print forward,strike,price,rate,tenor,sign, vmid  
            return vmid #EXIT CONDITION
        tprice = option_price_normal(forward,strike,vmid,rate,tenor,sign)
    return vmid
