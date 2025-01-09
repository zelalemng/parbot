# app/trading_bot.py
import logging
import time
import MetaTrader5 as mt5
from credentials import MT5_SERVER, MT5_LOGIN, MT5_PASSWORD, MT5_SYMBOL
from live_data import get_live_data
from strategy import buy_signal, sell_signal, apply_indicators

# Set up logging
logging.basicConfig(filename='trading_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
logging.info("Starting trading bot")

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed. Error code: ", mt5.last_error())
    logging.error("MT5 initialization failed")
else:
    print("MT5 initialized successfully")
    logging.info("MT5 initialized successfully")

    if not mt5.login(login=int(MT5_LOGIN), password=MT5_PASSWORD, server=MT5_SERVER):
        print("Login failed. Error code: ", mt5.last_error())
        logging.error(f"Login failed. Error code: {mt5.last_error()}")
    else:
        print("Logged into MT5 successfully")
        logging.info("Logged into MT5 successfully")

        symbol = MT5_SYMBOL

        def get_open_trades_count(symbol):
            trades = mt5.positions_get(symbol=symbol)
            return len(trades) if trades else 0

        def execute_trade(action, symbol, volume=0.01):
            print(f"Executing {action} trade")
            logging.info(f"Executing {action} trade")
            
            # Calculate stop-loss and take-profit levels
            tick = mt5.symbol_info_tick(symbol)
            price = tick.ask if action == 'buy' else tick.bid
            sl = price - 100 if action == 'buy' else price + 100  # Example: 200 points away
            tp = price + 200 if action == 'buy' else price - 200  # Example: 300 points away
            
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
                "type_time": mt5.ORDER_TIME_GTC,  # Good till canceled
                "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or Cancel
            }
            result = mt5.order_send(request)
            print(f"Trade result: {result}")
            logging.info(f'Trade result: {result}')
            logging.info(f'Order executed: retcode={result.retcode}, order={result.order}, deal={result.deal}, volume={result.volume}, price={result.price}')
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Trade failed with retcode: {result.retcode}")
                logging.error(f'Trade failed with retcode: {result.retcode}')

        previous_row = None

        while True:
            # Get live data
            df = get_live_data(symbol)
            if df is not None:
                df = apply_indicators(df)
                last_row = df.iloc[-1]
                print(f"Checking signals for last row: {last_row}")
                logging.info(f"Checking signals for last row: {last_row}")

                if previous_row is not None:
                    open_trades = get_open_trades_count(symbol)
                    if open_trades < 2:  # Check if the number of open trades is less than 2
                        if buy_signal(last_row, previous_row):
                            print("Buy signal detected")
                            logging.info("Buy signal detected")
                            execute_trade('buy', symbol)
                            logging.info("Buy signal executed")
                        else:
                            print("Buy signal not detected")
                            logging.info("Buy signal not detected")

                        if sell_signal(last_row, previous_row):
                            print("Sell signal detected")
                            logging.info("Sell signal detected")
                            execute_trade('sell', symbol)
                            logging.info("Sell signal executed")
                        else:
                            print("Sell signal not detected")
                            logging.info("Sell signal not detected")
                    else:
                        print("Max open trades reached. Waiting for trades to close.")
                        logging.info("Max open trades reached. Waiting for trades to close.")
                else:
                    print("Previous row is None, waiting for next data point.")
                    logging.info("Previous row is None, waiting for next data point.")
                
                previous_row = last_row
            else:
                print("Live data retrieval failed.")
                logging.error("Live data retrieval failed")

            # Wait for a specific interval before checking again
            time.sleep(5)  # Check every 5 seconds

    mt5.shutdown()
    logging.info("MT5 shutdown")
