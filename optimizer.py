import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import copy
import sys


def get_data(startdate, enddate, symbols):
  dt_timeofday = dt.timedelta(hours=16)
  ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)
  c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
  ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
  ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
  d_data = dict(zip(ls_keys, ldf_data))
  normalized_vals = d_data['close'].values / d_data['close'].values[0, :]
  return normalized_vals

def simulate(normalized_vals, percentage):
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
  if abs(inp.sum()-1.0)<0.00000001:
    return True
  else:
    return False

def get_percentages(inp, index, percentages):
  if (index == len(inp)):
    if(validate(inp)):
      percentages.append(copy.deepcopy(inp))
    return

  i = 0.0
  while (i < 1.1):
    inp[index] = i
    get_percentages(inp, index+1, percentages)
    i = i + 0.1

def best_portfolio(dt_start, dt_end, ls_symbols):
  percentages = list()
  get_percentages(np.zeros(len(ls_symbols)), 0, percentages)

  print str(len(percentages))

  normalized_vals = get_data(dt_start, dt_end, ls_symbols)
  print normalized_vals
  raw_input()
  
  bests = None
  bestp = None
  for p in percentages:
    v, ar, s, cr = simulate(normalized_vals, p)
    print "P: %s\tS: %s\tbests: %s\tbestp: %s\tar: %s" % (str(p), str(s), str(bests), str(bestp), str(ar)) 

    if bests == None:
      bests = s
      bestp = p
   
    if abs(s-bests)<0.00000001:
      print "SAME: P: %s\tS: %s" % (str(p), str(s))

    if s > bests:
      bests = s
      bestp = p

  return bestp

def main():
  print sys.argv
  if len(sys.argv) != 11:
    print "st_year st_month st_day end_year end_month end_day sym1 sym2 sym3 sym4"

  dt_start =  dt.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
  dt_end =  dt.datetime(int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
  ls_symbols = [sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10]]
  best_allocation = best_portfolio(dt_start, dt_end, ls_symbols)

  print "Best Allocation"
  print best_allocation

  volatility, average_d, sharpe, cumm_ret = simulate(get_data(dt_start, dt_end, ls_symbols), best_allocation)
  print "Sharpe: "+str(sharpe)
  print "Volatility: "+str(volatility)
  print "Average Daily Return: "+str(average_d)
  print "Cummulative Return: "+str(cumm_ret)

main()