import yfinance as yf
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import pandas as pd
import datetime as dt
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

def graph_data(ticker: str):
    dataframe = yf.download('AAPL', period="1y", auto_adjust=True, prepost=True, threads=True)
    
def get_yoy_price_data(ticker: str) :
    dataframe = yf.download('AAPL', period="1y", auto_adjust=True, prepost=True, threads=True)

    low = dataframe['High'].max()
    high= dataframe['Low'].min()
    
    last_yr = dt.date.today() - dt.timedelta(days=365)

    last_year_price = yf.download("AAPL", start=last_yr, end=last_yr+dt.timedelta(days=7))
    yoy = (get_last_price(ticker) - last_year_price['Close'][0]) / last_year_price['Close'][0]
    return low, high, yoy, last_year_price['Close'][0]

def get_last_price(ticker: str):
    session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)
    ticker = yf.Ticker(ticker, session=session)
    session.close()
    return ticker.history(period='1d')['Close'][0]
    
def get_company_name(ticker: str):
    return yf.Ticker(ticker).info['longName']


def get_relevant_put_options(stock : str, range: int):
    session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)
    ticker = yf.Ticker(stock, session=session)
    expirations = ticker.options
    last_price = ticker.history(period='1d')['Close'][0]
    
    low = last_price * (1-(range/100))
    high = last_price * (1+(range/100))
    
    below_strike = [] 
    above_strike = []
    for d in expirations:
        opt = ticker.option_chain(d).puts
        
        under_1 = opt.loc[opt['strike'] < low, 'strike'].max()
        under_2 = opt.loc[opt['strike'] > low, 'strike'].min()
        
        under = under_2 if abs(under_1 - low) > abs(under_2 - low) else under_1 
        
        over_1 = opt.loc[opt['strike'] > high, 'strike'].min()
        over_2 = opt.loc[opt['strike'] < high, 'strike'].max()
        over = over_2 if abs(over_1 - low) > abs(over_2 - low) else over_1
        
        under_row = opt.loc[opt['strike']==under].iloc[0]
        over_row = opt.loc[opt['strike']==over].iloc[0]
        under_row['Expiration'] = d
        over_row['Expiration'] = d
        
        '2024-08-16'
        days_to_exp = dt.datetime(int(d[:4]),int(d[5:7]),int(d[8:10])) - dt.datetime.now()
        
        under_row['Yield-to-Expiration-(%)'] = under_row['ask']*100 / (under_row['strike'])
        under_row['Annualized-Yield-(%)'] = (under_row['Yield-to-Expiration-(%)'] / (days_to_exp.days + 1)) * 365
        
        over_row['Yield-to-Expiration-(%)'] = over_row['ask']*100 / (under_row['strike'])
        over_row['Annualized-Yield-(%)'] = (over_row['Yield-to-Expiration-(%)'] / (days_to_exp.days + 1)) * 365
        
        below_strike.append(under_row)
        above_strike.append(over_row)
    
    print("below curr price")
    below_df = pd.DataFrame(below_strike)
    below_df = below_df.sort_values(by='Annualized-Yield-(%)', ascending=False)
    below_df = below_df.drop(['contractSymbol', 'lastTradeDate', 'change', 'percentChange', 'inTheMoney', 'contractSize', 'currency', 'lastPrice'], axis=1)
    below_df['Yield-to-Expiration-(%)'] = round(below_df['Yield-to-Expiration-(%)'], 3)
    below_df['Annualized-Yield-(%)'] = round(below_df['Annualized-Yield-(%)'], 3)
    below_df['impliedVolatility)'] = round(below_df['impliedVolatility'], 3)
    
    
    print("above curr price")
    above_df = pd.DataFrame(above_strike)
    above_df = above_df.sort_values(by='Annualized-Yield-(%)', ascending=False)
    above_df = above_df.drop(['contractSymbol', 'lastTradeDate', 'change', 'percentChange', 'inTheMoney', 'contractSize', 'currency', 'lastPrice'], axis=1)
    above_df['Yield-to-Expiration-(%)'] = round(above_df['Yield-to-Expiration-(%)'], 3)
    above_df['Annualized-Yield-(%)'] = round(above_df['Annualized-Yield-(%)'], 3)
    above_df['impliedVolatility)'] = round(above_df['impliedVolatility'], 3)
    
    print(below_df)
    print(above_df)
    session.close()
    return below_df, above_df


def get_relevant_call_options(stock : str, range: int):
    session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)
    ticker = yf.Ticker(stock, session=session)
    expirations = ticker.options
    last_price = ticker.history(period='1d')['Close'][0]
    
    low = last_price * (1-(range/100))
    high = last_price * (1+(range/100))
    
    below_strike = [] 
    above_strike = []
    for d in expirations:
        opt = ticker.option_chain(d).calls
        
        under_1 = opt.loc[opt['strike'] < low, 'strike'].max()
        under_2 = opt.loc[opt['strike'] > low, 'strike'].min()
        
        under = under_2 if abs(under_1 - low) > abs(under_2 - low) else under_1 
        
        over_1 = opt.loc[opt['strike'] > high, 'strike'].min()
        over_2 = opt.loc[opt['strike'] < high, 'strike'].max()
        over = over_2 if abs(over_1 - low) > abs(over_2 - low) else over_1
        
        under_row = opt.loc[opt['strike']==under].iloc[0]
        over_row = opt.loc[opt['strike']==over].iloc[0]
        under_row['Expiration'] = d
        over_row['Expiration'] = d
        
        '2024-08-16'
        days_to_exp = dt.datetime(int(d[:4]),int(d[5:7]),int(d[8:10])) - dt.datetime.now()
        
        under_row['Yield-to-Expiration-(%)'] = under_row['bid']*100 / (last_price)
        under_row['Annualized-Yield-(%)'] = (under_row['Yield-to-Expiration-(%)'] / (days_to_exp.days + 1)) * 365
        
        over_row['Yield-to-Expiration-(%)'] = over_row['bid']*100 / (last_price)
        over_row['Annualized-Yield-(%)'] = (over_row['Yield-to-Expiration-(%)'] / (days_to_exp.days + 1)) * 365
        
        below_strike.append(under_row)
        above_strike.append(over_row)
    
    print("below curr price")
    below_df = pd.DataFrame(below_strike)
    below_df = below_df.sort_values(by='Annualized-Yield-(%)', ascending=False)
    below_df = below_df.drop(['contractSymbol', 'lastTradeDate', 'change', 'percentChange', 'inTheMoney', 'contractSize', 'currency', 'lastPrice'], axis=1)
    below_df['Yield-to-Expiration-(%)'] = round(below_df['Yield-to-Expiration-(%)'], 3)
    below_df['Annualized-Yield-(%)'] = round(below_df['Annualized-Yield-(%)'], 3)
    below_df['impliedVolatility)'] = round(below_df['impliedVolatility'], 3)
    
    
    print("above curr price")
    above_df = pd.DataFrame(above_strike)
    above_df = above_df.sort_values(by='Annualized-Yield-(%)', ascending=False)
    above_df = above_df.drop(['contractSymbol', 'lastTradeDate', 'change', 'percentChange', 'inTheMoney', 'contractSize', 'currency', 'lastPrice'], axis=1)
    above_df['Yield-to-Expiration-(%)'] = round(above_df['Yield-to-Expiration-(%)'], 3)
    above_df['Annualized-Yield-(%)'] = round(above_df['Annualized-Yield-(%)'], 3)
    above_df['impliedVolatility)'] = round(above_df['impliedVolatility'], 3)
    
    print(below_df)
    print(above_df)
    session.close()
    return below_df, above_df

if __name__ == '__main__':
    # get_relevant_call_options('aapl', 10)

    dataframe = yf.download('AAPL', period="1y", auto_adjust=True, prepost=True, threads=True)

    max = dataframe['High'].max()
    min= dataframe['Low'].min()
    print(max)
    print(min)
    # low = data.fiftyTwoWeekLow
    # high = data.fiftyTwoWeekHigh
    
    # last_yr = dt.date.today() - dt.timedelta(days=365)
    # print(last_yr)
    # last_year_price = yf.download("AAPL", start=last_yr, end=last_yr+dt.timedelta(days=7))
    # print(last_year_price)
    # print(last_year_price['Close'][0])
