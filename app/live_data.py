# app/live_data.py
import MetaTrader5 as mt5
import pandas as pd

def get_live_data(symbol, timeframe=mt5.TIMEFRAME_M5, n=1000):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df
