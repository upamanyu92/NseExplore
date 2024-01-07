import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

# Example JSON data
example_data = {
    # ... (your JSON data here)
}

# Extracting stock data from the JSON
stock_data = example_data['data']

# Convert JSON data to a Pandas DataFrame
df = pd.DataFrame(stock_data)

# Extracting relevant features for modeling
features = [
    'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose',
    'ffmc', 'yearHigh', 'yearLow', 'totalTradedVolume', 'totalTradedValue',
    'nearWKH', 'nearWKL', 'perChange365d', 'perChange30d'
]

target = 'pChange'

# Selecting relevant columns
df = df[['symbol', 'timestamp'] + features + [target]]

# Convert timestamp to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sort DataFrame by timestamp
df = df.sort_values(by='timestamp')

# Splitting data into features and target variable
X = df[features]
y = df[target]

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

# Defining preprocessing steps
numeric_features = [
    'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose',
    'ffmc', 'yearHigh', 'yearLow', 'totalTradedVolume', 'totalTradedValue',
    'nearWKH', 'nearWKL', 'perChange365d', 'perChange30d'
]

numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

# Combining transformers using ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features)
    ])

# Applying preprocessing to training data
X_train_processed = preprocessor.fit_transform(X_train)

# Applying preprocessing to testing data
X_test_processed = preprocessor.transform(X_test)

# Model training (Random Forest Regressor as an example)
model = RandomForestRegressor(random_state=42)
model.fit(X_train_processed, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test_processed)

# Evaluate the model
mae = mean_absolute_error(y_test, y_pred)
print(f'Mean Absolute Error: {mae}')

# Plotting actual vs. predicted values over time
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df[target], label='Actual', marker='o')
plt.plot(X_test['timestamp'], y_pred, label='Predicted', marker='x')
plt.xlabel('Timestamp')
plt.ylabel('Percentage Change')
plt.title('Actual vs. Predicted Percentage Change Over Time')
plt.legend()
plt.show()
