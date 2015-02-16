#IMPORT log and sqrt FROM math MODULE
from math import log, sqrt, exp
#IMPORT date AND timedelta FOR HANDLING EXPIRY TIMES
from datetime import date, timedelta
#IMPORT SciPy stats MODULE
from scipy import stats

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

def option_price_normal(forward,strike,vol,rate,tenor,sign):
    if vol == 0:
        return sign * (forward - strike)   
    #sign = +1 for calls and -1 for puts
    d1 = (forward - strike) / (vol * sqrt(tenor)) 
    sameTerm = (vol * sqrt(tenor) * exp(-1*d1*d1/2)) / sqrt(2*3.141592653589793) 
    return exp(-1 * rate * tenor) * (sign * (forward - strike) * stats.norm.cdf(sign * d1) + sameTerm)  
 
def option_price_normal(forward,strike,vol,rate,tenor,sign):
def option_price_normal(forward,strike,vol,rate,tenor,sign):
def option_price_normal(forward,strike,vol,rate,tenor,sign):

def option_implied_vol_normal(forward,strike,price,rate,tenor,sign):
    #print 'imp vol calc:',forward,strike,price,rate,tenor,sign
    price_err_limit = price/10000
    iteration_limit = 20
    vmax = 1.0  #START SEARCH FOR UPPER VOL BOUND AT 100%
    tprice = 0
    while option_price(forward,strike,vmax,rate,tenor,sign) < price:
        vmax += 1
        if vmax > iteration_limit: return -1 #ERROR CONDITION
    #print 'vmax',vmax
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
        tprice = option_price_normal(forward,strike,vmid,rate,tenor,sign)
    #print 'imp_vol = ',vmid
    return vmid
