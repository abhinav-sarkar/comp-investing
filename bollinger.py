import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
from operator import itemgetter
import matplotlib.pyplot as plt

def initialize_dataframe(timestamps, symbols):
    data = np.zeros((len(timestamps), len(symbols)))
    ldf_portfolio = pd.DataFrame(
        data,
        columns=symbols,
        index=timestamps)
    return ldf_portfolio

def make_bollinger_band(d_data):
    data = initialize_dataframe(d_data.keys(), ['price', 'rmean', 'rstd'])
    data['price'] = d_data
    data['rmean'] = pd.rolling_mean(d_data, window=20);
    data['rstd'] = pd.rolling_std(d_data, window=20);

    pdata = initialize_dataframe(d_data.keys(), ['price', 'mean', 'upper', 'lower'])
    pdata['price'] = data['price']
    pdata['mean'] = data['rmean']
    pdata['lower'] = data['rmean'] - 2*data['rstd']
    pdata['upper'] = data['rmean'] + 2*data['rstd']

    pdata['bollv'] = (data['price']-data['rmean'])/data['rstd']
    
    plt.clf()
    plt.plot(d_data.keys(), pdata)
    plt.legend(['price', 'mean', 'upper', 'lower'])
    plt.ylabel('price')
    plt.xlabel('Date')
    plt.savefig('bollinger.pdf', format='pdf')
    print pdata
    return pdata


if __name__ == '__main__':
    ls_symbols = ['MSFT']
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    data = make_bollinger_band(d_data['close']['MSFT'])
    print "5/12"
    print data.ix[dt.datetime(2010, 5, 12)+dt.timedelta(hours=16)]

    print "5/21"
    print data.ix[dt.datetime(2010, 5, 21)+dt.timedelta(hours=16)]

    print "6/14"
    print data.ix[dt.datetime(2010, 6, 14)+dt.timedelta(hours=16)]

    print "6/23"
    print data.ix[dt.datetime(2010, 6, 23)+dt.timedelta(hours=16)]
