# app/strategy.py
import pandas as pd

def apply_indicators(df):
    # Calculate Parabolic SAR
    df['sar'] = calculate_parabolic_sar(df)
    return df

def calculate_parabolic_sar(df, af=0.02, amax=0.2):
    high = df['high']
    low = df['low']
    close = df['close']
    sar = [close.iloc[0]]
    ep = high.iloc[0]  # Extreme point
    af = af  # Acceleration factor

    long = True if close.iloc[1] > sar[0] else False

    for i in range(1, len(close)):
        if long:
            sar.append(sar[i-1] + af * (ep - sar[i-1]))
            if high.iloc[i] > ep:
                ep = high.iloc[i]
                af = min(amax, af + 0.02)
            if low.iloc[i] < sar[i]:
                sar[i] = ep
                ep = low.iloc[i]
                af = 0.02
                long = False
        else:
            sar.append(sar[i-1] + af * (ep - sar[i-1]))
            if low.iloc[i] < ep:
                ep = low.iloc[i]
                af = min(amax, af + 0.02)
            if high.iloc[i] > sar[i]:
                sar[i] = ep
                ep = high.iloc[i]
                af = 0.02
                long = True
    return sar

def buy_signal(current_row, previous_row):
    return current_row['close'] > current_row['sar'] and previous_row['close'] <= previous_row['sar']

def sell_signal(current_row, previous_row):
    return current_row['close'] < current_row['sar'] and previous_row['close'] >= previous_row['sar']
