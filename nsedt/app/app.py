# Please install dash version 0.23.0
# Please install dash_core_components version 1.6.0
# You should also have xlrd to read the Excel file.
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output
from nsedt import equity as eq

from nsedt.profit_predict_keras import get_profit_prediction
from nsedt.utils.utility import remove_null_values, get_inr

app = dash.Dash(__name__)

info_data = eq.get_companyinfo(format("TCS"))
# info_data = remove_null_values(info_data)
print(info_data.columns)
symbol = ["TCS", "INFY"]

custom_column_names = {
    'info': 'Info',
    'metadata': 'Metadata',
    'securityInfo': 'Security Info',
    'sddDetails': 'SDD Details',
    'priceInfo': 'Price Info',
    'industryInfo': 'Industry Info',
    'preOpenMarket': 'Pre-Open Market'
}

# Create a list of dictionaries for the 'columns' argument with custom column names
columns = [
    {
        'name': custom_column_names[key],  # Use custom column name for 'name' key
        'id': key  # Use key as the column identifier
    }
    for key in custom_column_names
]

# Format the layout
app.layout = html.Div([
    html.H1(children='Prediction Engine'),
    html.Div(children=[
        dash_table.DataTable(
            id='data-table',
            columns=[
            {'name': 'info', 'id': col} for col in info_data.columns
        ],
            data=info_data.to_dict('records')
        )
    ]),
    # In the tabs, indicate the type of interactive plot
    dcc.Tabs([
        dcc.Tab(label='Interactive stock profit prediction', children=[
            html.H3("Select stock code", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='stock_symbol',
                options=[{'label': i, 'value': i} for i in symbol],
                value=symbol[0],
                style={'textAlign': 'center', 'width': '250px', 'margin': 'auto'}),
            html.Br(),
            html.Hr(),
            html.Br(),
            html.Div(children=[
                html.Div(id='profit_info',
                         style={
                             'font-family': 'Arial',
                             'font-size': '18px',
                             'font-weight': 'bold',
                             'color': 'green',
                             'margin': '10px'
                         }),
                dcc.Interval(
                    id='stock_symbol',
                    interval=5 * 1000,  # Interval in milliseconds (5 seconds)
                    n_intervals=0
                )
            ])
        ]),
    ]),
    # dcc.Interval(id='stock_symbol', interval=5 * 1000)
])


# @app.callback(Output(component_id='stock_info', component_property='children'),
#               [Input(component_id='stock_symbol', component_property='value')])
# def update_output(value):
#     print(f"{eq.get_companyinfo(format(value))}")
#     return eq.get_companyinfo(format(value)).to_dict(orient="records")


@app.callback(Output(component_id='profit_info', component_property='children'),
              [Input(component_id='stock_symbol', component_property='n_intervals')])
def update_output2(value):
    start_date = date(2021, 1, 1)
    end_date = date(2023, 1, 10)
    stock_data = eq.get_price(start_date, end_date, symbol=symbol[0])
    stock_data.to_csv('stock_data.csv', index=False)
    print(value)
    return get_inr(get_profit_prediction(pd.read_csv('stock_data.csv'))[0])


if __name__ == '__main__':
    app.run_server(debug=True)
