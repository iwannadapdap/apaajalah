# Importing libraries 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import configparser
from twisted.internet import reactor 
import pandas as pd
import time

# Loading keys from config file
config = configparser.ConfigParser()
config.read_file(open('secret.cfg'))
actual_api_key = config.get('BINANCE', 'ACTUAL_API_KEY')
actual_secret_key = config.get('BINANCE', 'ACTUAL_SECRET_KEY')

#create the client object and connect to Binance
client = Client(actual_api_key, actual_secret_key)
#client.get_account()

def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback+' min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time','Open','High','Low','Close','Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


#trading strategy
#buy if asset fell more than 0.2% within the last 30min
#sell if asset rises by more then 0.15% or falls further by 0.15%
def strategytest(symbol, qty, entried=False):
    while not (entried == True):
        df = getminutedata(symbol, '1m', '30m')
        cumulret = (df.Open.pct_change() +1).cumprod() - 1
        if not entried:
           # if cumulret[-1] < -0.001:
                order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                print(order)
                entried=True
           # else:
           #     print('No  Trade has been executed')
        if entried:
            while True:
                df = getminutedata(symbol, '1m','30m')
                sincebuy = df.loc[df.index > pd.to_datetime(order['transactTime'], unit='ms')]
                if len(sincebuy) > 0:
                    sincebuyret = (sincebuy.Open.pct_change() +1).cumprod() -1
                    if sincebuyret[-1] > 0.003 or sincebuyret[-1] < -0.03:
                        order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                        print(order)
                        break
        time.sleep(5)

#client.create_order(symbol='BTCUP', side='BUY', type='MARKET', quantiy=0.2)

while True:
    strategytest('BTCUPUSDT', 0.15)


