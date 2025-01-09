import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
from app.credentials import MT5_SERVER, MT5_LOGIN, MT5_PASSWORD, MT5_SYMBOL
from app.live_data import get_live_data
from app.strategy import buy_signal, sell_signal, apply_indicators

# Function to login to MT5
def login_mt5(server, login, password):
    if not mt5.initialize():
        st.error("MT5 initialization failed")
        return False
    if not mt5.login(login=int(login), password=password, server=server):
        st.error("MT5 login failed")
        return False
    st.success("Logged into MT5 successfully")
    return True

# Function to execute trades
def execute_trade(action, symbol, volume, sl_points, tp_points):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if action == 'buy' else tick.bid
    sl = price - sl_points if action == 'buy' else price + sl_points
    tp = price + tp_points if action == 'buy' else price - tp_points

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 234000,
        "comment": "Automated trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    return result

# Streamlit app layout
st.title("MT5 Trading Bot")
st.sidebar.header("Settings")

server = st.sidebar.text_input("MT5 Server", MT5_SERVER)
login = st.sidebar.text_input("MT5 Login", MT5_LOGIN)
password = st.sidebar.text_input("MT5 Password", MT5_PASSWORD, type="password")
symbol = st.sidebar.text_input("Symbol", MT5_SYMBOL)
volume = st.sidebar.number_input("Volume", value=0.01, min_value=0.01)
sl_points = st.sidebar.number_input("Stop Loss Points", value=100, min_value=1)
tp_points = st.sidebar.number_input("Take Profit Points", value=200, min_value=1)
timeframe = st.sidebar.selectbox("Timeframe", [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_D1])

if st.sidebar.button("Start Bot"):
    if login_mt5(server, login, password):
        st.session_state['running'] = True

if st.sidebar.button("Stop Bot"):
    mt5.shutdown()
    st.session_state['running'] = False
    st.success("Bot stopped")

if 'running' in st.session_state and st.session_state['running']:
    st.success("Bot is running")
    df = get_live_data(symbol, timeframe)
    if df is not None:
        df = apply_indicators(df)
        st.write(df.tail())
else:
    st.warning("Bot is not running")

# Handling trade execution
if st.button("Execute Buy Trade"):
    result = execute_trade('buy', symbol, volume, sl_points, tp_points)
    st.write(f"Trade result: {result}")

if st.button("Execute Sell Trade"):
    result = execute_trade('sell', symbol, volume, sl_points, tp_points)
    st.write(f"Trade result: {result}")

st.sidebar.text("Developed with ❤️ by your friendly AI assistant")
