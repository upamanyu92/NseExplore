import pandas as pd
import dash
from dash import dcc, html, Output, Input
import plotly.graph_objects as go
import requests

from nsedt.utils.Options import OptionChainResponse


# Function to fetch historical option chain data from NSE API
def fetch_option_chain_data():
    print('Fetching option chain data...')
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.nseindia.com',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception if the response status is not 200
        data = response.json()
        return OptionChainResponse(records=data['records'], other_data=data['filtered'])
    except requests.exceptions.RequestException as e:
        print("Failed to fetch data:", e)
        return []

# Function to fetch live Nifty indices price
def fetch_nifty_price():
    print('Fetching Nifty price...')
    url = 'https://www.nseindia.com/api/quote-equity?symbol=NIFTY'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.nseindia.com',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception if the response status is not 200
        data = response.json()
        nifty_price = data['data'][0]['lastPrice']
        return nifty_price
    except requests.exceptions.RequestException as e:
        print("Failed to fetch Nifty price:", e)
        return None

# Function to process option chain data and calculate support and resistance levels
def analyze_option_chain(option_data):
    if not option_data:
        return None

    records = option_data.records
    print(records.get)
    call_data = pd.DataFrame()
    put_data = pd.DataFrame(records.records.data.PE)

    # Calculate potential support and resistance levels based on open interest
    support_levels_ = call_data[['strikePrice', 'openInterest']].sort_values(by='openInterest', ascending=False).head(5)
    resistance_levels_ = put_data[['strikePrice', 'openInterest']].sort_values(by='openInterest', ascending=False).head(5)

    return support_levels_, resistance_levels_

# Function to get data for a specific time (e.g., 09:30:00)
def get_buyers_sellers_quantity(option_data, target_duration):
    # Initialize counters for buyers_info and sellers_info
    buyers_info = 0
    sellers_info = 0
    print('Counting buyers_info and sellers_info...')
    # Loop through the option data to count buyers_info and sellers_info
    for item in option_data:
        if 'CE' in item:
            ce_data = item['CE']
            # print(ce_data)
            if ce_data:
                buyers_info += ce_data['openInterest'] - ce_data['changeinOpenInterest']
                sellers_info += ce_data['changeinOpenInterest']
        if 'PE' in item:
            pe_data = item['PE']
            # print(pe_data)
            if pe_data:
                buyers_info += pe_data['openInterest'] - pe_data['changeinOpenInterest']
                sellers_info += pe_data['changeinOpenInterest']

    return buyers_info, sellers_info


def update_graph_data(n):
    data = fetch_option_chain_data()
    time = '09:30:00'
    records = data.records
    buyers_info, sellers_info = get_buyers_sellers_quantity(records, time)
    # Analyze option chain data
    support_levels_, resistance_levels_ = analyze_option_chain(data)
    return [buyers_info, sellers_info, support_levels_, resistance_levels_]

# Initialize Dash app
app = dash.Dash(__name__)

# Create the bar graph for Buyers vs. Sellers
labels = ['Buyers', 'Sellers']
colors = ['blue', 'red']
buyers, sellers, support_levels, resistance_levels = update_graph_data(0)
fig1 = go.Figure(data=[go.Bar(x=labels, y=[buyers, sellers], marker_color=colors)])
fig1.update_layout(title='Quantity of Buyers and Sellers at 09:30:00', xaxis_title='Type', yaxis_title='Quantity')

# Create the line graph for Nifty indices price
nifty_price = fetch_nifty_price()
fig2 = go.Figure(data=[go.Scatter(x=[0], y=[nifty_price], mode='lines+markers')])
fig2.update_layout(title='Nifty Indices Price', xaxis_title='Time', yaxis_title='Price')

# Plot support and resistance levels
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=support_levels['strikePrice'], y=support_levels['openInterest'],
                         mode='markers', name='Support', marker=dict(color='green', size=10)))
fig3.add_trace(go.Scatter(x=resistance_levels['strikePrice'], y=resistance_levels['openInterest'],
                         mode='markers', name='Resistance', marker=dict(color='red', size=10)))

fig3.update_layout(title='Potential Support and Resistance Levels from Option Chain',
                  xaxis_title='Strike Price', yaxis_title='Open Interest')

# Define the app layout
app.layout = html.Div([
    html.H1('NSE Nifty Option Chain Data and Nifty Indices Price', style={'text-align': 'center'}),
    html.Div([
        dcc.Graph(id='buyer-seller-graph', figure=fig1),
        dcc.Graph(id='nifty-price-graph', figure=fig2),
        dcc.Graph(id='support-resistance-graph', figure=fig3)
    ]),
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # in milliseconds, update every 10 seconds
        n_intervals=0
    )
])

# Define the callback to update the graphs
@app.callback(
    [Output('buyer-seller-graph', 'figure'),
     Output('nifty-price-graph', 'figure')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    buyers, sellers, support_levels, resistance_levels = update_graph_data(0)
    fig1 = go.Figure(data=[go.Bar(x=labels, y=[buyers, sellers])])
    fig1.update_layout(title='Quantity of Buyers and Sellers at 09:30:00', xaxis_title='Type', yaxis_title='Quantity')

    nifty_price = fetch_nifty_price()
    fig2 = go.Figure(data=[go.Scatter(x=[0], y=[nifty_price], mode='lines+markers')])
    fig2.update_layout(title='Nifty Indices Price', xaxis_title='Time', yaxis_title='Price')

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=support_levels['strikePrice'], y=support_levels['openInterest'],
                              mode='markers', name='Support', marker=dict(color='green', size=10)))
    fig3.add_trace(go.Scatter(x=resistance_levels['strikePrice'], y=resistance_levels['openInterest'],
                              mode='markers', name='Resistance', marker=dict(color='red', size=10)))

    fig3.update_layout(title='Potential Support and Resistance Levels from Option Chain',
                       xaxis_title='Strike Price', yaxis_title='Open Interest')

    return fig1, fig2, fig3

# Run the app
if __name__ == '__main__':
    app.run_server(port=8053)
