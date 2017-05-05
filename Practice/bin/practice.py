import datetime as dt
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import numpy as np
from finsymbols import symbols

# web.DataReader('^GSPC','yahoo')  # S&P 500
# web.DataReader('^IXIC','yahoo')  # NASDAQ
# web.DataReader('^DJI','yahoo')   # Dow

def calc_return(x):
    x[1:, :] = (x[1:, :] / x[0:-1]) - 1
    x[0, :] = np.zeros(x.shape[1])
    return x;

def calc_cumulative_return(x):
    return x/x[0]

def calc_std_deviation(x):
    return [np.std(x[:,i]) for i in range(x.shape[1])];

def get_symbols():
    sp_500 = symbols.get_sp500_symbols()
    symbolList = list()

    for e in sp_500:
        symbolList.append(e.get("symbol"))

    return symbolList

def get_cheap_stocks(dt_start, dt_end, limit):
    ls_symbols =np.array(get_symbols())
    df = pdr.get_data_yahoo(ls_symbols, dt_start, dt_end).to_frame(filter_observations=False)
    df = df[df['Adj Close'] < limit]
    groups = df.groupby(level='minor')
    df = groups.apply(lambda g: g[g['Adj Close'] == g['Adj Close'].max()])
    return df.index.get_level_values(0).values

def get_stocks(dt_start, dt_end, limit):
    ls_symbols =np.array(get_symbols())
    df = pdr.get_data_yahoo(ls_symbols, dt_start, dt_end).to_frame()
    groups = df.groupby(level='minor', group_keys=False, as_index=False)
    df = groups.apply(lambda g: close_filter(g, limit))
    df.sort_index(level=0, inplace=True)
    return df.to_panel()

def cum_filter(df):
    if df['Cum Return'].max() > 5:
        return df

def close_filter(df, limit):
    if df['Adj Close'].max() < limit:
        return df

def stock_analysis():
    dt_start = dt.datetime(2009, 1, 1)
    dt_end = dt.datetime(2017, 12, 31)

    stock_panel = get_stocks(dt_start, dt_end, 50)
    adj_close_values = stock_panel['Adj Close'].values

    stock_df = stock_panel.to_frame(filter_observations=False)

    returns = calc_return(np.array(adj_close_values))
    cuml_returns = calc_cumulative_return(np.array(adj_close_values))

    stock_df['Return'] = returns.ravel()
    stock_df['Cum Return'] = cuml_returns.ravel()

    # df = df.drop(df[df['Cum Return'] < 1].index.get_level_values('minor'), level='minor')

    groups = stock_df.groupby(level=1, group_keys=False, as_index=False)
    df = groups.apply(lambda g: cum_filter(g))

    symbols_list = df.index.get_level_values(1).unique().values
    dates_list = df.index.get_level_values(0).unique().values

    return_list = []
    cum_return_list = []
    gb = df.groupby(level=0)

    for d in dates_list:
        return_list.append(gb.get_group(d)['Return'].values)
        cum_return_list.append(gb.get_group(d)['Cum Return'].values)

    return_array = np.array(return_list)
    cum_return_array = np.array(cum_return_list)

    # std_deviation = calc_std_deviation(returns)
    # print(std_deviation)
    #

    plt.clf()

    f, (ax1, ax2, ax3) = plt.subplots(3)
    ax1.plot(dates_list, adj_close_values)
    ax1.xaxis_date()
    ax1.set_ylabel('Adj Close')
    ax1.set_xlabel('date')
    ax1.legend(symbols_list)

    ax2.plot(dates_list, return_array)
    ax2.xaxis_date()
    ax2.set_ylabel('daily return')
    ax2.set_xlabel('date')
    ax2.legend(symbols_list)

    ax3.plot(dates_list, cum_return_array)
    ax3.xaxis_date()
    ax3.set_ylabel('cumulative return')
    ax3.set_xlabel('date')
    ax3.legend(symbols_list)

    if symbols_list.size > 0:
        f.autofmt_xdate()
        plt.show()

stock_analysis()