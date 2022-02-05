import time
import pyupbit
import datetime
import numpy as np

access = "acc"
secret = "sec"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma(ticker, ma):
    """ma일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=ma)
    ma_result = df['close'].rolling(ma).mean().iloc[-1]
    return ma_result

def get_hma(ticker, ma, k):
    """ma일 hma 조회"""
    ma = int(ma)
    ma2 = int(ma//2)
    maq = int(np.sqrt(int(ma)))
    df = pyupbit.get_ohlcv(ticker, interval="day", count=230)
    df['wma_ma'] = df['close'].rolling(ma).apply(lambda x: ((np.arange(ma)+1)*x).sum()/(np.arange(ma)+1).sum(), raw=True)
    df['wma_ma//2'] = df['close'].rolling(ma2).apply(lambda x: ((np.arange(ma2)+1)*x).sum()/(np.arange(ma2)+1).sum(), raw=True)
    df['hmabase'] = df['wma_ma//2']*2 - df['wma_ma']
    df['hma_ma'] = df['hmabase'].rolling(maq).apply(lambda x: ((np.arange(maq)+1)*x).sum()/(np.arange(maq)+1).sum(), raw=True)
    hma = df['hma_ma'].iloc[-k]
    return hma

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=20):
            target_price = get_target_price("KRW-ETH", 0.6)
            current_price = get_current_price("KRW-ETH")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-ETH", krw*0.9995)
        else:
            eth = get_balance("ETH")
            hma100 = get_hma("KRW-ETH", 100, 1)
            hma99 = get_hma("KRW-ETH", 100, 2)
            vix = float(hma100/hma99)
            current_price = get_current_price("KRW-ETH")
            ma20 = get_ma("KRW-ETH", 20)
            ma10 = get_ma("KRW-ETH", 10)
            ma3 = get_ma("KRW-ETH", 3)
            if ((eth > 0.001) and (vix > 1.005) and (current_price < ma10)):
                upbit.sell_market_order("KRW-ETH", eth*0.9995)
            elif ((eth>0.001) and (vix <= 1.005) and (ma20 < ma3) and (current_price < ma10)):
                upbit.sell_market_order("KRW-ETH", eth*0.9995)
            elif ((eth>0.001) and (vix <= 1.005) and (ma20 > ma3) and  (current_price < ma3)):
                upbit.sell_market_order("KRW-ETH", eth*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)


#변수 출력 테스트
# target_price = get_target_price("KRW-ETH", 0.6)
# current_price = get_current_price("KRW-ETH")
# eth = get_balance("ETH")
# hma100 = get_hma("KRW-ETH", 100, 1)
# hma99 = get_hma("KRW-ETH", 100, 2)
# vix = float(hma100/hma99)
# current_price = get_current_price("KRW-ETH")
# ma10 = get_ma("KRW-ETH", 10)
# ma3 = get_ma("KRW-ETH", 3)
# ma20 = get_ma("KRW-ETH", 20)

# print("T : ",target_price,", C : ", current_price,", E : ",  eth,", H100 : ",  hma100,", H99 : ",  hma99,", V : ",  vix,", M10 : ",  ma10,", M3 : ",  ma3,",V true : ",((eth>0.001) and (vix <= 1.005) and (current_price < ma3)))
# print(ma20)