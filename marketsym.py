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

	orders_csv_reader = csv.DictReader(orders_csv.splitlines(), fieldnames=('year', 'month' , 'day', 'symbol', 'action', 'units'))

	orders = list()
	for row in orders_csv_reader:
		row['datetime'] = dt.datetime(int(row['year']), int(row['month']), int(row['day']))
		orders.append(copy.deepcopy(row))

	orders_dict = dict()
	for row in orders:
		i = row['datetime']+dt.timedelta(hours=16)
		if i in orders_dict.keys():
			orders_dict[i].append(row)
		else:
			val = list()
			val.append(row)
			orders_dict[i] = val

	return orders, orders_csv, orders_dict

def main():
	cash = sys.argv[1]
	orders, orders_csv, orders_dict = process_csv(sys.argv[2])

	# generate date ranges
	ldt_timestamps = du.getNYSEdays(orders[0]['datetime'], orders[-1]['datetime']+dt.timedelta(days=1), dt.timedelta(hours=16))

	# get prices
	symbols = set()
	for row in orders:
		symbols.add(row['symbol'])
	dataobj = da.DataAccess('Yahoo')
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(ldt_timestamps, list(symbols), ls_keys)

	ldf_portfolio = initialize_dataframe(ldt_timestamps, list(symbols))
	ldf_cash = initialize_dataframe(ldt_timestamps, ['Cash'])

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