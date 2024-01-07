import threading
import time
import json
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output


from nsedt.api.equity_api import fetch_indices, fetch_and_update_data
from nsedt.utils import load_cookie, get_headers
from nsedt.utils.JSONNormalizer import JSONNormalizer
import pandas as pd


# Step 1: Define the stock index model class
class StockIndexModel:
    def __init__(self, json_data):
        self.name = json_data.get("name", "")
        self.advance = json_data.get("advance", {})
        self.timestamp = json_data.get("timestamp", "")
        self.data = [StockDataModel(item) for item in json_data.get("data", [])]
        self.metadata = json_data.get("metadata", {})
        self.market_status = json_data.get("marketStatus", {})
        self.date_30d_ago = json_data.get("date30dAgo", "")
        self.date_365d_ago = json_data.get("date365dAgo", "")

    def to_dataframe(self):
        data_list = [data.to_dict() for data in self.data]
        dataframe = pd.DataFrame(data_list)
        dataframe["index_name"] = self.name
        dataframe["timestamp"] = self.timestamp
        return dataframe

class StockDataModel:
    def __init__(self, data):
        self.priority = data.get("priority", 0)
        self.symbol = data.get("symbol", "")
        self.identifier = data.get("identifier", "")
        self.series = data.get("series", "")
        self.open = data.get("open", 0.0)
        self.day_high = data.get("dayHigh", 0.0)
        self.day_low = data.get("dayLow", 0.0)
        self.last_price = data.get("lastPrice", 0.0)
        self.previous_close = data.get("previousClose", 0.0)
        self.change = data.get("change", 0.0)
        self.p_change = data.get("pChange", 0.0)
        self.total_traded_volume = data.get("totalTradedVolume", 0)
        self.total_traded_value = data.get("totalTradedValue", 0.0)
        self.last_update_time = data.get("lastUpdateTime", "")
        self.year_high = data.get("yearHigh", 0.0)
        self.ffmc = data.get("ffmc", 0.0)
        self.year_low = data.get("yearLow", 0.0)
        self.near_wkh = data.get("nearWKH", 0.0)
        self.near_wkl = data.get("nearWKL", 0.0)
        self.per_change_365d = data.get("perChange365d", 0.0)
        self.date_365d_ago = data.get("date365dAgo", "")
        self.chart_365d_path = data.get("chart365dPath", "")
        self.date_30d_ago = data.get("date30dAgo", "")
        self.per_change_30d = data.get("perChange30d", 0.0)
        self.chart_30d_path = data.get("chart30dPath", "")
        self.chart_today_path = data.get("chartTodayPath", "")
        self.meta = data.get("meta", {})

    def to_dict(self):
        data_dict = vars(self).copy()
        del data_dict["meta"]  # Exclude 'meta' attribute
        return data_dict


# Step 2: Load the JSON data from the text file
def load_json_from_file(filepath):
    with open(filepath, "r") as file:
        try:
            json_normalizer = JSONNormalizer()
            json_string = json_normalizer.normalize_json(file.read())
            json_string = json_string.replace("None", "null")
            json_string = json_string.replace("True", "true").replace("False", "false")
            json_data = json.loads(json_string, parse_constant=custom_converter)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {filepath}: {e}")
            return None

def custom_converter(value):
    return value if value.lower() != 'null' else None

data_dir = os.path.join(os.path.dirname(__file__), "api/data")

def read_data_from_files():
    data = pd.DataFrame()

    for filename in os.listdir(data_dir):
        if filename.endswith("_output_data.txt"):
            filepath = os.path.join(data_dir, filename)
            json_data = load_json_from_file(filepath)
            if json_data:
                stock_index = StockIndexModel(json_data)
                data = stock_index.to_dataframe()

    return data


# Step 3: Create a Dash app to display the loaded stock index data
app = dash.Dash(__name__)

# Initialize variables
cookies = load_cookie()
indices = fetch_indices()



df = read_data_from_files()
print(df.columns)

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Stock Data Dashboard"),

    # Metadata Section
    html.Div([
        html.H2("Metadata"),
        html.Div([
            html.Strong("Index Name: "), df["index_name"].iloc[0],
            html.Br(),
            html.Strong("last_price: "), df["last_price"].iloc[0],
        ]),
    ]),

    # Stock Table Section
    html.Div([
        html.H2("Stock Table"),
        dash_table.DataTable(
            id='stock-table',
            columns=[],  # Columns will be dynamically updated
            data=[],
            style_table={'height': '400px', 'overflowY': 'auto'}
        ),
    ]),

    # Button to refresh stock data
    html.Button("Refresh Data", id="refresh-button", n_clicks=0),


    # Interval to update the data every 10 seconds
    dcc.Interval(
        id='interval-component',
        interval=10 * 60 * 1000,  # in milliseconds
        n_intervals=0
    )
])


def update_data():
    global data
    while True:
        for index in indices:
            fetch_and_update_data(index, get_headers(), data_dir)
        time.sleep(600)  # Wait for 10 minutes before fetching again


# Start the data update thread
update_thread = threading.Thread(target=update_data)
update_thread.start()


# Callback to update stock table data
@app.callback(Output('stock-table', 'data'),
    [Input('refresh-button', 'n_clicks')])
def update_stock_table(n_clicks):
    global data
    if n_clicks > 0:
        for index in indices:
            fetch_and_update_data(index, get_headers(), data_dir)

        # Set n_clicks back to 0 to avoid repeated updates
        n_clicks = 0

    if data is None:
        return [], []

    columns = [{"name": key, "id": key} for key in data.columns]
    table_data = data.to_dict('records')

    return columns, table_data

if __name__ == '__main__':
    app.run_server(debug=True)
