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
  orders_file = open(sys.argv[2]).read()
  orders = csv.DictReader(orders_file.splitlines(), fieldnames=('year', 'month' , 'day', 'symbol', 'action', 'units'))
  
  for row in orders:
    row['datetime'] = dt.datetime(int(row['year']), int(row['month']), int(row['day']))

  for row in orders:
    print row




if __name__ == '__main__':
	main()