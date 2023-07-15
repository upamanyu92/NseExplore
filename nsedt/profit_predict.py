import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


def predict_max_profit(symbol):
    # Download stock data
    stock = yf.download(symbol, start='2010-01-01', end='2023-07-16')

    # Prepare the data
    stock['NextDayClose'] = stock['Close'].shift(-1)
    stock.dropna(inplace=True)
    X = stock[['Open', 'High', 'Low', 'Close', 'Volume']]
    y = stock['NextDayClose']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Train the linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Visualize the predicted vs actual prices
    plt.figure(figsize=(10, 6))
    plt.plot(y_test.values, label='Actual')
    plt.plot(y_pred, label='Predicted')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Stock Price Prediction')
    plt.legend()
    plt.show()

    # Predict the next day's closing price
    last_day = stock.iloc[-1]
    prediction = model.predict([last_day[['Open', 'High', 'Low', 'Close', 'Volume']]])

    return prediction[0]


# Example usage
stock_symbol = 'AAPL'  # Replace with your desired stock symbol
predicted_price = predict_max_profit(stock_symbol)
print(f"The predicted closing price for {stock_symbol} is: ${predicted_price:.2f}")
