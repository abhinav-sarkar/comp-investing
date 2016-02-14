import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import copy

def simulate(startdate, enddate, symbols, percentage):
  dt_timeofday = dt.timedelta(hours=16)
  ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)

  c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
  ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
  ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
  d_data = dict(zip(ls_keys, ldf_data))


  normalized_vals = d_data['close'].values / d_data['close'].values[0, :]
  indiv_daily_value = percentage*normalized_vals
  total_dv = indiv_daily_value.sum(axis=1)
  
  #calculate daily return
  #print total_dv
  B = total_dv[1:]
  A = total_dv[0:-1]
  C = (B/A)-1
  dailyret = np.zeros(C.shape[0]+1)
  dailyret[1:] = C
  #print np.average(dailyret)
  sharpe = (math.sqrt(252)*np.average(dailyret))/np.std(dailyret)
  #print sharpe
  return (np.std(dailyret), np.average(dailyret), sharpe, (total_dv[-1]/total_dv[0]))

def validate(inp):
  print inp
  print "returning = "+str(inp.sum() == 1.0)
  return (inp.sum() == 1)

def get_percentages(inp, index, percentages):
  if (index == len(inp)):
    if(validate(inp)):
      percentages.append(copy.deepcopy(inp))
    return

  i = 0.0
  while (i <= 1.0):
    inp[index] = i
    get_percentages(inp, index+1, percentages)
    i = i + .1

def best_portfolio(dt_start, dt_end, ls_symbols):
  percentages = list()
  get_percentages(np.zeros(len(ls_symbols)), 0, percentages)

  bests = None
  bestp = None
  for p in percentages:
    v, ar, s, cr = simulate(dt_start, dt_end, ls_symbols, p)
    
    if bests == None:
      bests = s
      bestp = p 
   
    if s > bests:
      bests = s
      bestp = p

  print "Best Allocation"
  print bestp

#ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
ls_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
percentage = [0, 0, 0, 1]
#print "volatility, average_ret, sharpe, cumm_ret"
best_portfolio(dt_start, dt_end, ls_symbols)




#na_price = d_data['close'].values
#plt.clf()
#plt.plot(ldt_timestamps, na_price)
#plt.legend(ls_symbols)
#plt.ylabel('Adjusted Close')
#plt.xlabel('Date')
#plt.savefig('adjustedclose.pdf', format='pdf')
