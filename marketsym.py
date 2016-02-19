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

if __name__ == '__main__':
	main()