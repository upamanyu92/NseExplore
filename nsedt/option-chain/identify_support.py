import requests
import pandas as pd
import plotly.graph_objects as go

# Function to fetch option chain data from NSE API
def fetch_option_chain_data():
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch option chain data.")
        return None

# Function to process option chain data and calculate support and resistance levels
def analyze_option_chain(option_data):
    if not option_data:
        return None

    records = option_data['records']['data']
    call_data = pd.DataFrame(records['CE'])
    put_data = pd.DataFrame(records['PE'])

    # Calculate potential support and resistance levels based on open interest
    support_levels_ = call_data[['strikePrice', 'openInterest']].sort_values(by='openInterest', ascending=False).head(5)
    resistance_levels_ = put_data[['strikePrice', 'openInterest']].sort_values(by='openInterest', ascending=False).head(5)

    return support_levels_, resistance_levels_

# Fetch option chain data from NSE API
option_chain_data = fetch_option_chain_data()

# Analyze option chain data
support_levels, resistance_levels = analyze_option_chain(option_chain_data)

# Print potential support and resistance levels
print("Potential Support Levels:")
print(support_levels)

print("\nPotential Resistance Levels:")
print(resistance_levels)

# Plot support and resistance levels
fig = go.Figure()
fig.add_trace(go.Scatter(x=support_levels['strikePrice'], y=support_levels['openInterest'],
                         mode='markers', name='Support', marker=dict(color='green', size=10)))
fig.add_trace(go.Scatter(x=resistance_levels['strikePrice'], y=resistance_levels['openInterest'],
                         mode='markers', name='Resistance', marker=dict(color='red', size=10)))

fig.update_layout(title='Potential Support and Resistance Levels from Option Chain',
                  xaxis_title='Strike Price', yaxis_title='Open Interest')

# Show the plot
fig.show()
