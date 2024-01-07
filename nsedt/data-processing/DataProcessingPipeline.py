import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

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

# Splitting data into features and target variable
X = df[features]
y = df[target]

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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

# Print the processed data
print("Processed Training Data:")
print(pd.DataFrame(X_train_processed, columns=numeric_features).head())

print("\nProcessed Testing Data:")
print(pd.DataFrame(X_test_processed, columns=numeric_features).head())
