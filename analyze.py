import csv, sys
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import copy

def get_normalized(data):
	
def get_statistics(vals, percentage):
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

def add_datetime(data):
	timestamps = list(data.index)
	test = pd.DataFrame(
		timestamps,
		columns=["test"],
		index = timestamps)
	data['Year'] = test.applymap(lambda x: x.year)
	data['Month'] = test.applymap(lambda x: x.month)
	data['Day'] = test.applymap(lambda x: x.day)
	return data

def initialize_dataframe(timestamps, symbols):
	data = np.zeros((len(timestamps), len(symbols)))
	ldf_portfolio = pd.DataFrame(
		data,
		columns=symbols,
		index=timestamps)
	return ldf_portfolio

def process_csv(filename):
	orders_csv = None
	with open(filename) as f:
		orders_csv = f.read()

	orders_csv_reader = csv.DictReader(
		orders_csv.splitlines(),
		fieldnames=('year', 'month' , 'day', 'value'))

	orders = list()
	for row in orders_csv_reader:
		row['datetime'] = dt.datetime(int(row['year']), int(row['month']), int(row['day']))
		orders.append(copy.deepcopy(row))

	return orders, orders_csv

def main():
	vals, vals_csv = process_csv(sys.argv[1])

	# generate date ranges
	ldt_timestamps = du.getNYSEdays(orders[0]['datetime'], orders[-1]['datetime']+dt.timedelta(days=1), dt.timedelta(hours=16))

	# get prices
	symbols = list()
	symbols.add(sys.argv[2])
	dataobj = da.DataAccess('Yahoo')
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(
		ldt_timestamps,
		symbols,
		ls_keys)

	d_data = dict(zip(ls_keys, ldf_data))

	prices = d_data['close']

	ldf_cash['Cash'].ix[ldt_timestamps[0]] = cash
	for i in xrange(0,len(ldt_timestamps)):
		if i > 0:
			ldf_cash['Cash'].ix[ldt_timestamps[i]] = ldf_cash['Cash'].ix[ldt_timestamps[i-1]]
			for sym in symbols:
				ldf_portfolio[sym].ix[ldt_timestamps[i]] = ldf_portfolio[sym].ix[ldt_timestamps[i-1]]

		if ldt_timestamps[i] in orders_dict.keys():
			for event in orders_dict[ldt_timestamps[i]]:
				eventsymbol = event['symbol'].upper()
				symbolprice = prices[eventsymbol].ix[ldt_timestamps[i]]
				eventunits = int(event['units'])
				eventprice = eventunits*symbolprice
				if event['action'].lower() == 'buy':
					ldf_cash['Cash'].ix[ldt_timestamps[i]] = float(ldf_cash['Cash'].ix[ldt_timestamps[i]]) - eventprice
					ldf_portfolio[eventsymbol].ix[ldt_timestamps[i]] = int(ldf_portfolio[eventsymbol].ix[ldt_timestamps[i]]) + eventunits
				else:
					ldf_cash['Cash'].ix[ldt_timestamps[i]] = float(ldf_cash['Cash'].ix[ldt_timestamps[i]]) + eventprice
					ldf_portfolio[eventsymbol].ix[ldt_timestamps[i]] = int(ldf_portfolio[eventsymbol].ix[ldt_timestamps[i]]) - eventunits

	stockvalues = prices*ldf_portfolio
	values = initialize_dataframe(ldt_timestamps, ['StockValues'])
	values['StockValues'] = stockvalues.sum(axis=1)
	values['Cash'] = ldf_cash['Cash']
	values['Total'] = values.sum(axis=1)
	add_datetime(values)
	values.to_csv('output.csv',
		columns=('Year', 'Month', 'Day', 'Total'),
		index=False)

if __name__ == '__main__':
	main()


def get_data(startdate, enddate, symbols):
	dt_timeofday = dt.timedelta(hours=16)
	ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)
	c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))
	normalized_vals = d_data['close'].values / d_data['close'].values[0, :]
	return normalized_vals


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

	dt_start =	dt.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
	dt_end =	dt.datetime(int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
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