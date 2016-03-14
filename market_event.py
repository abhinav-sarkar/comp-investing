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

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

def find_events(ls_symbols, d_data, p, orders):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print "Finding Events - %f" % p

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            if f_symprice_today < p and f_symprice_yest >= p:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                orders.append([ldt_timestamps[i], s_sym, 'Buy', 100])
                orders.append([ldt_timestamps[min(i+5,len(ldt_timestamps)-1)], s_sym, 'Sell', 100])

    return df_events


if __name__ == '__main__':
    #for data in ['sp5002008', 'sp5002012']:
    for data in ['sp5002012']:
        dt_start = dt.datetime(2008, 1, 1)
        dt_end = dt.datetime(2009, 12, 31)
        ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

        dataobj = da.DataAccess('Yahoo')
        ls_symbols = dataobj.get_symbols_from_list(data)
        ls_symbols.append('SPY')

        ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
        ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
        d_data = dict(zip(ls_keys, ldf_data))

        for s_key in ls_keys:
            d_data[s_key] = d_data[s_key].fillna(method='ffill')
            d_data[s_key] = d_data[s_key].fillna(method='bfill')
            d_data[s_key] = d_data[s_key].fillna(1.0)

        for price in [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
            orders = list();
            df_events = find_events(ls_symbols, d_data, price, orders)
            with open('market-orders-%s.csv' % price, 'w') as a:
                for t in sorted(orders, key=itemgetter(0)):
                    a.write("%s,%s,%s,%s,%s,%s,\n" % (t[0].year, t[0].month, t[0].day, t[1], t[2], t[3]))

            print "Creating Study data - %s, price - %f" % (data, price)
            filename = "EventStudy-%s-%s.pdf" % (data, str(price))
            ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename=filename, b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
