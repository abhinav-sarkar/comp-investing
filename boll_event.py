import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

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
    return pdata

def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['close']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    df_spy_bollb = make_bollinger_band(d_data['close']['SPY'])
    for s_sym in ls_symbols:
        df_sym_bollb = make_bollinger_band(d_data['close'][s_sym])
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symboll_today = df_sym_bollb['bollv'].ix[ldt_timestamps[i]]
            f_symboll_yest = df_sym_bollb['bollv'].ix[ldt_timestamps[i - 1]]
            f_marketboll_today = df_spy_bollb['bollv'].ix[ldt_timestamps[i]]
            f_marketprice_yest = df_spy_bollb['bollv'].ix[ldt_timestamps[i - 1]]

            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            #print f_symboll_today
            #print f_symboll_yest
            #print f_marketboll_today
            #raw_input()
            if f_symboll_today <=-2.0 and f_symboll_yest > -2.0 and f_marketboll_today >= 1.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


if __name__ == '__main__':
    for data in ['sp5002012']:
        dt_start = dt.datetime(2008, 1, 1)
        dt_end = dt.datetime(2009, 12, 31)
        ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

        print "Getting Data"
        dataobj = da.DataAccess('Yahoo')
        ls_symbols = dataobj.get_symbols_from_list(data)
        ls_symbols.append('SPY')

        ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
        ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
        d_data = dict(zip(ls_keys, ldf_data))
        print "Got Data"

        for s_key in ls_keys:
            d_data[s_key] = d_data[s_key].fillna(method='ffill')
            d_data[s_key] = d_data[s_key].fillna(method='bfill')
            d_data[s_key] = d_data[s_key].fillna(1.0)

        df_events = find_events(ls_symbols, d_data)
        print "Creating Bolinger Study data"
        filename = "EventStudy-Bollinger"
        ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
            s_filename=filename, b_market_neutral=True, b_errorbars=True,
            s_market_sym='SPY')