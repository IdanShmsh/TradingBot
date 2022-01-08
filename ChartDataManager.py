import time
import threading
import yfinance as yf
from logger import send_log_message as log

"""
this script is used to actively get the real time charts' data for the program to use.
for each interval it gets its data once every 'this interval' where its meaningless to
get the data more frequent than it updates publicly. (get the data for 15m chart every
15 minutes...)
The data collected using the yfinance package, the program gets it as a dataframe which it than stores
as a pickle file for the rest of the program to access and use.

Though it's much less efficient, the reason I do it this way is to separate this process
from the main process. I want to let this processes to be independent from each other so
that this can continuously run untouched even in cases of failure or manual stop of the main
process.
"""

print("Chart Data Manager: Starting...")

charts = [
    'EURUSD',
    'EURGBP',
    'EURAUD',
    'EURNZD',
    'EURCAD',
    'EURCHF',
    'GBPUSD',
    'AUDUSD',
    'NZDUSD',
    'USDCAD',
    'USDCHF',
    'USDJPY',
    'AUDCAD',
    'AUDCHF',
    'AUDJPY',
    'AUDNZD',
    'CADCHF',
    'CADJPY',
    'CHFJPY',
    'EURJPY',
    'GBPAUD',
    'GBPCAD',
    'GBPCHF',
    'GBPJPY',
    'GBPNZD',
    'NZDCAD',
    'NZDCHF',
    'NZDJPY',
    'USDSGD',
    'AUDSGD',
    'EURSGD',
    'GBPSGD',
    'CHFDKK',
    'CHFSEK',
    'EURDKK',
    'EURNOK',
    'EURPLN',
    'EURSEK',
    'EURZAR',
    'GBPDKK',
    'GBPNOK',
    'GBPSEK',
    'GBPZAR',
    'USDCNH',
    'USDDKK',
    'USDHKD',
    'USDMXN',
    'USDNOK',
    'USDPLN',
    'USDSEK',
    'USDZAR',
    'SGDJPY',
    'DKKNOK',
    'SEKNOK',
]

chart_num = len(charts)

busy_loading = False

# when initialized to make all the charts initially up to date, get the data for all of them
def get_data_for_all_charts():
    i = 0
    for c in charts:
        i += 1
        print("\r", "Chart Data Manager: getting data for all charts - [" + str(int(100 * (i / chart_num))) + "%]", end="")
        try:
            data = yf.download(tickers=c + '=X', period='5d', interval='5m', progress=False)
            data.drop('Volume', axis=1, inplace=True)
            data.drop('Adj Close', axis=1, inplace=True)
            data.to_pickle("Chart_Data_Files/" + c + "-5m" + ".pkl")
            data = yf.download(tickers=c + '=X', period='15d', interval='15m', progress=False)
            data.drop('Volume', axis=1, inplace=True)
            data.drop('Adj Close', axis=1, inplace=True)
            data.to_pickle("Chart_Data_Files/" + c + "-15m" + ".pkl")
            data = yf.download(tickers=c + '=X', period='30d', interval='30m', progress=False)
            data.drop('Volume', axis=1, inplace=True)
            data.drop('Adj Close', axis=1, inplace=True)
            data.to_pickle("Chart_Data_Files/" + c + "-30m" + ".pkl")
        except:
            log('an error occurred while trying to get chart data - probably a connection error', False)

    print("\n")

# every 5 minutes, get the data only for the 5m charts
def feed_data_for_5m_charts():
    global busy_loading
    while(True):
        time.sleep(5 * 60 - 25)
        while busy_loading:
            time.sleep(1)
        busy_loading = True
        i = 0
        for c in charts:
            i += 1
            print("\r", "Chart Data Manager: feeding 5m data - [" + str(int(100 * (i / chart_num))) + "%]", end="")
            try:
                data = yf.download(tickers=c + '=X', period='5d', interval='5m', progress=False)
                data.drop('Volume', axis=1, inplace=True)
                data.drop('Adj Close', axis=1, inplace=True)
                data.to_pickle("Chart_Data_Files/" + c + "-5m" + ".pkl")
            except:
                log('an error occurred while trying to get chart data - probably a connection error', False)
                continue

        busy_loading = False
        print("\n")

# every 15 minutes, get the data only for the 15m charts
def feed_data_for_15m_charts():
    global busy_loading
    while(True):
        time.sleep(15 * 60 - 25)
        while busy_loading:
            time.sleep(1)
        busy_loading = True
        i = 0
        for c in charts:
            i += 1
            print("\r", "Chart Data Manager: feeding 15m data - [" + str(int(100 * (i / chart_num))) + "%]", end="")
            try:
                data = yf.download(tickers=c + '=X', period='15d', interval='15m', progress=False)
                data.drop('Volume', axis=1, inplace=True)
                data.drop('Adj Close', axis=1, inplace=True)
                data.to_pickle("Chart_Data_Files/" + c + "-15m" + ".pkl")
            except:
                log('an error occurred while trying to get chart data - probably a connection error', False)
                continue
        busy_loading = False
        print("\n")

# every 30 minutes, get the data only for the 30m charts
def feed_data_for_30m_charts():
    global busy_loading
    while(True):
        time.sleep(30 * 60 - 25)
        while busy_loading:
            time.sleep(1)
        busy_loading = True
        i = 0
        for c in charts:
            i += 1
            print("\r", "Chart Data Manager: feeding 30m data - [" + str(int(100 * (i / chart_num))) + "%]", end="")
            try:
                data = yf.download(tickers=c + '=X', period='30d', interval='30m', progress=False)
                data.drop('Volume', axis=1, inplace=True)
                data.drop('Adj Close', axis=1, inplace=True)
                data.to_pickle("Chart_Data_Files/" + c + "-30m" + ".pkl")
            except:
                log('an error occurred while trying to get chart data - probably a connection error', False)
                continue
        busy_loading = False
        print("\n")

#get the data for all charts first
get_data_for_all_charts()

print("Chart Data Manager: Finished.")
print("Chart Data Manager: Initializing data feed loops...")

# start the data feed loops as threads working in parallel to each other
#than starts the treads that feed the data continuesly to the charts data
t = threading.Thread(target=feed_data_for_5m_charts, args=())
t.start()
t = threading.Thread(target=feed_data_for_15m_charts, args=())
t.start()
t = threading.Thread(target=feed_data_for_30m_charts, args=())
t.start()

print("Chart Data Manager: Finished.")
print("Chart Data Manager: Data feed is up and running.")
print("Chart Data Manager: Processes that use chart data are allowed to begin running")
print("=====================================")