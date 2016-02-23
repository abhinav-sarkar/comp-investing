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
	normalized_vals = data.values / data.values[0, :]
	return normalized_vals
	
def get_statistics(data):
	#print data
	B = data[1:]
	#print B
	A = data[0:-1]
	#print A
	C = (B/A)-1
	#print C
	dailyret = np.zeros(((C.shape[0]+1), 1))
	#print dailyret
	dailyret[1:, :] = C[:, :]
	#print dailyret
	#print np.average(dailyret)
	sharpe = (math.sqrt(252)*np.average(dailyret))/np.std(dailyret)
	#print sharpe
	return (np.std(dailyret), np.average(dailyret), sharpe, (data[-1]/data[0])[0])

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

def initialize_dataframe(timestamps, symbols, data=None):
	if data == None:
		data = np.zeros((len(timestamps), len(symbols)))

	ldf_portfolio = pd.DataFrame(
		data,
		columns=symbols,
		index=timestamps)
	return ldf_portfolio

def process_csv(filename):
	daily_csv = None
	with open(filename) as f:
		daily_csv = f.read()

	daily_csv_reader = csv.DictReader(
		daily_csv.splitlines(),
		fieldnames=('year', 'month' , 'day', 'value'))

	daily = list()
	for row in daily_csv_reader:
		row['datetime'] = dt.datetime(int(row['year']), int(row['month']), int(row['day']))
		daily.append(copy.deepcopy(row))

	return daily, daily_csv

def main():
	vals, vals_csv = process_csv(sys.argv[1])

	# generate date ranges
	ldt_timestamps = du.getNYSEdays(
		vals[0]['datetime'],
		vals[-1]['datetime']+dt.timedelta(days=1),
		dt.timedelta(hours=16))

	# get prices
	symbols = list()
	symbols.append(sys.argv[2])
	#print symbols
	dataobj = da.DataAccess('Yahoo')
	ls_keys = ['close']
	ldf_data = dataobj.get_data(
		ldt_timestamps,
		symbols,
		ls_keys)

	data = list()
	for val in vals:
		data.append(float(val['value']))

	np_data = np.asarray(data)
	np_data = np_data.reshape((len(data),1))
	data_df = initialize_dataframe(ldt_timestamps, ['Data'], np_data)

	d_data = dict(zip(ls_keys, ldf_data))
	prices = d_data['close']

	#print prices
	#print values

	v, ar, s, cr = get_statistics(get_normalized(copy.deepcopy(prices)))
	v1, ar1, s1, cr1 = get_statistics(get_normalized(copy.deepcopy(data_df)))

	print "Data Range :  %s to  %s" % (ldt_timestamps[0], ldt_timestamps[-1])

	print "Sharpe Ratio of Fund : %s" % s1
	print "Sharpe Ratio of $SPX : %s" % s

	print "Total Return of Fund : %s" % cr1
	print "Total Return of $SPX : %s" % cr

	print "Standard Deviation of Fund : %s" % v1
	print "Standard Deviation of $SPX : %s" % v

	print "Average Daily Return of Fund : %s" % ar1
	print "Average Daily Return of $SPX : %s" % ar

if __name__ == '__main__':
	main()