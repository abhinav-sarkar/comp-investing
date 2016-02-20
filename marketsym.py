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



def main():
	cash = sys.argv[1]
	orders_csv = None
	with open(sys.argv[2]) as f:
		orders_csv = f.read()

	orders_csv_reader = csv.DictReader(orders_csv.splitlines(), fieldnames=('year', 'month' , 'day', 'symbol', 'action', 'units'))

	orders = list()
	for row in orders_csv_reader:
		row['datetime'] = dt.datetime(int(row['year']), int(row['month']), int(row['day']))
		orders.append(row)

	# generate date ranges
	ldt_timestamps = du.getNYSEdays(orders[0]['datetime'], orders[-1]['datetime'], dt.timedelta(hours=16))

	# get prices
	dataobj = da.DataAccess('Yahoo')
	symbols = set()
	for row in orders:
		symbols.add(row['symbol'])

	dataobj = da.DataAccess('Yahoo')
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(ldt_timestamps, list(symbols), ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	


if __name__ == '__main__':
	main()