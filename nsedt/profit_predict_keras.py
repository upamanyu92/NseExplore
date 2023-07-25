import numpy as np
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler


# from nsedt.utils.get_nse_symbols import get_stock_codes

# nse_symbols = get_stock_codes()

def get_profit_prediction(data):
    # Preprocess the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close Price'].values.reshape(-1, 1))

    # Define the training data
    train_data = scaled_data[:int(0.8 * len(data))]
    test_data = scaled_data[int(0.8 * len(data)):]

    # Function to create sequences for training/testing
    def create_sequences(data_in, sequence_length_in):
        x = []
        y = []
        for i in range(len(data_in) - sequence_length_in):
            x.append(data_in[i:i + sequence_length_in])
            y.append(data_in[i + sequence_length_in])
        return np.array(x), np.array(y)

    # Define sequence length and create sequences
    sequence_length = 30
    x_train, y_train = create_sequences(train_data, sequence_length)
    x_test, y_test = create_sequences(test_data, sequence_length)

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(x_train, y_train, epochs=10, batch_size=32)

    # Make predictions
    train_predictions = model.predict(x_train)
    test_predictions = model.predict(x_test)

    # Inverse scaling
    train_predictions = scaler.inverse_transform(train_predictions)
    y_train = scaler.inverse_transform(y_train)
    test_predictions = scaler.inverse_transform(test_predictions)
    y_test = scaler.inverse_transform(y_test)

    # Calculate the maximum profit from predictions
    train_profit = max(train_predictions - y_train)
    test_profit = max(test_predictions - y_test)
    profit_model: list = [train_profit, test_profit]
    return profit_model
