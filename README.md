# nse data

Introduction

This is python library to provide API on advanced prediction and live stock analysis data.

---
## Run

```py

from nsedt.api import equity as eq
from datetime import date

start_date = date(2022, 1, 1)
end_date = date(2023, 1, 10)
print(eq.get_price(start_date, end_date, symbol="TCS"))
start_date = "01-05-2023"
end_date = "03-05-2023"
print(eq.get_corpinfo(start_date, end_date, symbol="TCS"))
print(eq.get_event(start_date, end_date))
print(eq.get_event())
print(eq.get_marketstatus())
print(eq.get_marketstatus(response_type="json"))
print(eq.get_companyinfo(symbol="TCS"))
print(eq.get_companyinfo(symbol="TCS", response_type="json"))
print(eq.get_chartdata(symbol="TCS"))

```
---
## Output
```sh
# get_price
        Date  Open Price  High Price  Low Price  Close Price  ...  52 Week High Price  52 Week Low Price     VWAP  Deliverable Volume  Deliverable Percent
0   2022-01-03      3750.0     3830.00    3745.00      3817.75  ...              3989.9             2880.0  3807.43             1433211                61.09
..         ...         ...         ...        ...          ...  ...                 ...                ...      ...                 ...                  ...
104 2023-01-04      3306.7     3327.35    3286.20      3314.65  ...              4043.0             2926.1  3306.45              778260                63.19

# get_corpinfo
symbol series ind faceVal                                            subject  ... ndStartDate                               comp          isin ndEndDate caBroadcastDate
0    TCS     EQ   -       1                         Dividend - Rs 22 Per Share  ...           -  Tata Consultancy Services Limited  INE467B01029         -            None
3    TCS     EQ   -       1  Interim Dividend - Rs 8 Per Share Special Divi...  ...           -  Tata Consultancy Services Limited  INE467B01029         -            None

# get_event
        symbol                                   company  ...                                            bm_desc         date
0       5PAISA                    5Paisa Capital Limited  ...  To consider and approve the financial results ...  01-May-2023
56  ANTGRAPHIC                        Antarctica Limited  ...  Antarctica Limited has informed the Exchange t...  03-May-2023

#get_companyinfo
                                               info                           metadata securityInfo  ... priceInfo   industryInfo preOpenMarket
symbol                                           TCS                                TCS          NaN  ...       NaN            NaN           NaN
atoSellQty                                       NaN                                NaN          NaN  ...       NaN            NaN           491

#get_companyinfo json format
{"info":{"symbol":"TCS","companyName":"Tata Consultancy Services Limited","industry":"COMPUTERS - SOFTWARE","activeSeries":["EQ"],"debtSeries":[],"tempSuspendedSeries":[],"isFNOSec":true,"isCASec":false,"isSLBSec":true,"isDebtSec":false,"isSuspended":false,"isETFSec":false,"isDelisted":false, ......}

#get_marketstatus

           market marketStatus     tradeDate     index_eq     last  ... percentChange marketStatusMessage   expiryDate underlying tradeDateFormatted
0  Capital Market        Close   09-Jun-2023  NIFTY 50  18563.4  ...         -0.38    Market is Closed          NaN        NaN                NaN
4  currencyfuture        Close  Invalid date            82.4975  ...                  Market is Closed  16-Jun-2023     USDINR        09-Jun-2023


#get_chartdata
                 0        1
0    1686301201000  3300.00
404  1686301620000  3250.00


```
---

# API Documentation

## Functions

### ```profit_predict_keras.py```

Returns best possible profit from a stock
## Output
```Epoch 1/10
6/6 [==============================] - 2s 15ms/step - loss: 0.0736
Epoch 2/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0228
Epoch 3/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0153
Epoch 4/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0151
Epoch 5/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0116
Epoch 6/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0108
Epoch 7/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0104
Epoch 8/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0097
Epoch 9/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0097
Epoch 10/10
6/6 [==============================] - 0s 14ms/step - loss: 0.0097
6/6 [==============================] - 0s 3ms/step
1/1 [==============================] - 0s 13ms/step
Maximum profit in training set: [272.49257812]
Maximum profit in test set: [109.25371094]
```

### get_companyinfo

Function description goes here.

### get_marketstatus

Function description goes here.

### get_price

Function description goes here.

### get_corpinfo

Function description goes here.

### get_event

Function description goes here.

### get_chartdata

Function description goes here.

# Option Chain Prediction

`/nsedt/option-chain/call-predict.py`

## Usage:

1. Set Index Mode or Stock Mode

2. Select your Index or Stock

3. Select its Expiry Date

4. Enter your preferred Strike Price

5. Set the interval you want the program to refresh (Optional : Defaults to 1 minute)

6. Click Start

## Notes:

- If there is an error in fetching dates on login screen then try refreshing

- If there is an error in fetching dates on main screen then try stopping and again starting from option menu

- If you face any issue or have a suggestion then feel free to open an issue.

- It is recommended to enable logging and then send the `NSE-OCA.log` file or the console output for reporting issues

- In case of network or connection errors the program doesn't crash and will keep retrying until manually stopped

- If a `ZeroDivisionError` occurs or some data doesn't exist the value of the variable will be defaulted to `0`

- Set `load_nse_icon` option to `False` in the configuration file to prevent downloading the NSE icon in the `.py`
  version to speed up loading time

- If an `Incorrect Strike Price` error message is displayed and the strike price you entered is correct then check
  whether the NSE website is loading the data properly before creating an issue

## Features:

- The program continuously retrieves and refreshes the option chain giving near real-time analysis to the traders

- New data rows are added only if the NSE server updates its time or data (To prevent displaying duplicate data)

- Supported Indices and
  Stocks: https://www.nseindia.com/products-services/equity-derivatives-list-underlyings-information

- Option Chain data source: https://www.nseindia.com/option-chain

- Supports multiple instances with different indices/stocks and/or strike prices selected

- Red and Green colour indication for data based on trends

- Toast Notifications for notifying when trend changes (Windows 10 and 11 only). Notified changes:
    * Open Interest: Bullish/Bearish
    * Open Interest Upper Boundary Strike Prices: Change in Value
    * Open Interest Lower Boundary Strike Prices: Change in Value
    * Call Exits: Yes/No
    * Put Exits: Yes/No
    * Call ITM: Yes/No
    * Put ITM: Yes/No

- Program title format: `NSE-Option-Chain-Analyzer - {index/stock} - {expiry_date} - {strike_price}`

- Stop and Start manually

- You can select all table data using Ctrl+A or select individual cells, rows and columns

- Then you can copy it using Ctrl+C or right click menu

- You can then paste it in any spreadsheet application (Tested with MS Excel and Google Sheets)

- Export table data to `.csv` file

- Real time exporting data rows to `.csv` file

- Dumping entire Option Chain data to a `.csv` file

- Auto stop the program at 3:30pm when the market closes

- Alert if the last time the data from the server was updated is 5 minutes or more

- Auto Checking for updates

- Debug Logging

- Saves certain settings in a configuration file for subsequent runs. Saved Settings:
    * Load App Icon
    * Index/Stock Mode
    * Selected Index
    * Selected Stock
    * Refresh Interval
    * Live Export
    * Notifications
    * Dump entire Option Chain
    * Auto stop at 3:30pm
    * Warn Late Server Updates
    * Auto Check for Updates
    * Debug Logging

- Keyboard shortcuts for all options

## Data Displayed

> #### Table Data:

| Data                   | Description                                                                                                                                                                                                                                                                             |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Server Time            | Indicates last data update time by NSE server                                                                                                                                                                                                                                           |
| Value                  | Underlying Instrument Value indicates the value of the underlying Security or Index                                                                                                                                                                                                     |
| Call Sum               | Calculated. Sum of the Changes in Call Open Interest contracts of the given Strike Price and the next immediate two Strike Prices (In Thousands for Index Mode and Tens for Stock Mode)                                                                                                 |
| Put Sum                | Calculated. Sum of the Change in Put Open Interest contracts of the given Strike Price and the next two Strike Prices (In Thousands for Index Mode and Tens for Stock Mode)                                                                                                             |
| Difference             | Calculated. Difference between the Call Sum and Put Sum. If it's very -ve it's bullish, if it's very +ve then it's bearish else it's a sideways session.                                                                                                                                |
| Call Boundary          | Change in Call Open Interest contracts for 2 Strike Prices above the given Strike Price. This is used to determine if Call writers are taking new positions (Bearish) or exiting their positions (Bullish). (In Thousands for Index Mode and Tens for Stock Mode)                       |
| Put Boundary           | Change in Put Open Interest for the given Strike Price. This is used to determine if Put writers are taking new positions (Bullish) or exiting their positions(Bearish). (In Thousands for Index Mode and Tens for Stock Mode)                                                          |
| Call In The Money(ITM) | This indicates that bullish trend could continue and Value could cross 4 Strike Prices above given Strike Price. It's calculated as the ratio of Put writing and Call writing at the 4th Strike Price above the given Strike price. If the absolute ratio > 1.5 then it's bullish sign. |
| Put In The Money(ITM)  | This indicates that bearish trend could continue and Value could cross 2 Strike Prices below given Strike Price. It's calculated as the ratio of Call writing and Put writing at the 2nd Strike Price below the given Strike price. If the absolute ratio > 1.5 then it's bearish sign. |

> #### Label Data:

| Data                         | Description                                                                                                                                                                                                                                                                                                                                                                                                                 |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Open Interest Upper Boundary | Highest and 2nd Highest(highest in OI boundary range) Call Open Interest contracts (In Thousands for Index Mode and Tens for Stock Mode) and their corresponding Strike Prices                                                                                                                                                                                                                                              |
| Open Interest Lower Boundary | Highest and 2nd Highest(highest in OI boundary range) Put Open Interest contracts (In Thousands for Index Mode and Tens for Stock Mode) and their corresponding Strike Prices                                                                                                                                                                                                                                               |
| Open Interest                | This indicates if the latest OI data record indicates Bearish or Bullish signs near Indicated Strike Price. If the Call Sum is more than the Put Sum then the OI is considered Bearish as there is more Call writing than Puts. If the Put Sum is more than the Call sum then the OI Is considered Bullish as the Put writing exceeds the Call writing.                                                                     |
| Put Call Ratio(PCR)          | Sum Total of Put Open Interest contracts divided by Sum Total of Call Open Interest contracts                                                                                                                                                                                                                                                                                                                               |
| Call Exits                   | This indicates if the Call writers are exiting near given Strike Price in the latest OI data record. If the Call sum is < 0 or if the change in Call OI at the Call boundary (2 Strike Prices above the given Strike Price) is < 0, then Call writers are exiting their positions and the Bulls have a clear path.                                                                                                          |
| Put Exits                    | This indicates if the Put writers are exiting near given Strike Price in the latest OI data record. If the Put sum is < 0 or if the change in Put OI at the Put boundary (the given Strike Price) is < 0, then Put writers are exiting their positions and the Bears have a clear path.                                                                                                                                     |
| Call In The Money(ITM)       | This indicates if the Call writers are also exiting far OTM strike prices (4 Strike Prices above the given Strike Price) showing extreme bullishness. Conditions are if the Call writers are exiting their far OTM positions and the Put writers are writing at the same Strike Price & if the absolute ratio > 1.5 then it's bullish sign. This signal also changes to Yes if the change in Call OI at the far OTM is < 0. |
| Put In The Money(ITM)        | This indicates if the Put writers are also exiting far OTM strike prices (2 Strike Prices below the given Strike Price) showing extreme bearishness. Conditions are if the Put writers are exiting their far OTM positions and the Call writers are writing at the same Strike Price & if the absolute ratio > 1.5 then it's a bearish sign. This signal also changes to Yes if the change in Put OI at the far OTM is < 0. |

## Screenshots:

- Login Page:

  <br>![Login_Window](https://i.imgur.com/x3leqmZ.png) <br><br>

- Main Window Index Mode:

  <br>![Main_Window_Index](https://i.imgur.com/ZFQCxCK.png) <br><br>

- Main Window Stock Mode:

  <br>![Main_Window_Stock](https://i.imgur.com/qd8CLol.png) <br><br>

- Selecting Data:

  <br>![Selecting_Data](https://i.imgur.com/zOjptS2.png) <br><br>

- Option Menu:

  <br>![Option_Menu](https://i.imgur.com/CocgjbN.png) <br><br>

- Toast Notifications (Windows 10 and 11 only):

  <br>![Notification](https://i.imgur.com/d3Fokxo.png) <br><br>

## Dependencies:

- [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) is used for compiling the program to a .exe file

- [pandas](https://pypi.org/project/pandas/) are used for storing and manipulating the data

- [requests](https://pypi.org/project/requests/) is used for accessing and retrieving data from the NSE website

- [stream-to-logger](https://pypi.org/project/streamtologger/) is used for debug logging

- [tksheet](https://pypi.org/project/tksheet/) is used for the table containing the data

- [win10toast](https://pypi.org/project/win10toast/) is used for toast notifications on Windows 10 and 11



