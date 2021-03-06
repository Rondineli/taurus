import time

import config
import database
import prediction
import lstm
import yscrapper

import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr


def stocks_prediction(prediction_days, stock):
    print(f"Executing prediction for {stock}")
    yf.pdr_override()
    now = time.strftime('%Y-%m-%d', time.localtime(time.time()+86400))
    data = pdr.get_data_yahoo(stock, start=config.HISTORY_START_DATE, end=now)
    db = database.Database()
    db.use("taurus")
    db.panda_write("taurus", data, stock)


    # Save Simple Prediction to DB
    prediction_results = prediction.simple_prediction(prediction_days, data)
    simple_data = _save("Prediction", prediction_results, stock)

    model = lstm.model(prediction_days, data)
    # Save LSTM Prediction to DB
    lstm_results = lstm.predict(model[0], model[1], model[2], model[3], model[4])
    lstm_data = _save("LSTMPrediction", lstm_results, stock)

    # Save Root Deviation to DB
    rmse_results = lstm.root_deviation(lstm_results, model[0])
    # The var writing is on the opposite way so I can generate a query on influxdb for all the deviations.
    _save(stock, rmse_results, "Deviation")

    return simple_data, lstm_data


def _save(tablename, results, stock):
    day_time = time.time()
    result = {}
    db = database.Database()
    db.use("taurus")
    for single_prediction in results:
        day_time = day_time +  86400 # Seconds in a day
        date = time.strftime('%Y-%m-%d', time.localtime())

        if tablename == "LSTMPrediction":
            result[date] = single_prediction[0]
        else:
            result[date] = single_prediction

        df = pd.DataFrame(list(result.items()), columns = ['Date', tablename])
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.set_index(df['Date'])
        df = df.drop(['Date'], axis=1)
        db.panda_write("taurus", df, stock)
        #df.to_csv(header=None, index=False).strip('\n').split('\n')
    
    return df



# get stock info
#print(stock.info)
## get historical market data
#hist = stock.history(period="max")
#print(hist)
#
## show actions (dividends, splits)
#print(stock.actions)
#
## show dividends
#stock.dividends
#
## show splits
#stock.splits
#
## show financials
#stock.financials
#stock.quarterly_financials
#
## show major holders
#stock.major_holders
#
## show institutional holders
#stock.institutional_holders
#
## show balance heet
#stock.balance_sheet
#stock.quarterly_balance_sheet
#
## show cashflow
#stock.cashflow
#stock.quarterly_cashflow
#
## show earnings
#stock.earnings
#stock.quarterly_earnings
#
## show sustainability
#stock.sustainability

# show analysts recommendations
#print(stock.recommendations)

## show next event (earnings, etc)
#stock.calendar
#
## show ISIN code - *experimental*
## ISIN = International Securities Identification Number
#stock.isin
#
## show options expirations
#stock.options

# get option chain for specific expiration
#opt = stock.option_chain('2020-07-31')
# data available via: opt.calls, opt.puts