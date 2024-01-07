import configparser
import os
import sys
from datetime import datetime
from typing import List, TextIO, Optional, Dict, Tuple, Any
import oc_web_service
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

import requests

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def create_error_window():
    error_window = html.Div([
        html.H1("NSE-Option-Chain-Analyzer"),
        html.P("Failed to fetch Symbols.\nThe program will now exit."),
    ], style={"text-align": "center", "margin-top": "40vh"})
    return error_window


class Nse:
    version: str = '5.5'

    def __init__(self) -> None:
        self.intervals: List[int] = [1, 2, 3, 5, 10, 15]
        self.stdout: TextIO = sys.stdout
        self.stderr: TextIO = sys.stderr
        self.previous_date: Optional[datetime.date] = None
        self.previous_time: Optional[datetime.time] = None
        self.time_difference_factor: int = 5
        self.first_run: bool = True
        self.stop: bool = False
        self.dates: List[str] = [""]
        self.indices: List[str] = []
        self.stocks: List[str] = []
        self.url_oc: str = "https://www.nseindia.com/option-chain"
        self.url_index: str = "https://www.nseindia.com/api/option-chain-indices?symbol="
        self.url_stock: str = "https://www.nseindia.com/api/option-chain-equities?symbol="
        self.url_symbols: str = "https://www.nseindia.com/api/underlying-information"
        self.url_icon_png: str = "https://github.com/upamanyu92/NseExplore/blob/main/nsedt/option-chain/nse_logo.png"
        self.url_icon_ico: str = "https://github.com/upamanyu92/NseExplore/blob/main/nsedt/option-chain/nse_logo.ico"
        self.url_update: str = "https://api.github.com/repos/upamanyu92/" \
                               "NseExplore/releases/latest"
        self.headers: Dict[str, str] = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}
        self.session: requests.Session = requests.Session()
        self.cookies: Dict[str, str] = {}
        self.config_parser: configparser.ConfigParser = configparser.ConfigParser()
        self.create_config(new=True) if not os.path.isfile('NSE-OCA.ini') else None
        self.get_config()
        self.log() if self.logging else None
        self.units_str: str = 'in K' if self.option_mode == 'Index' else 'in 10s'
        self.output_columns: [str, str, str, str, str, str, str, str, str] = [
            'Time', 'Value', f'Call Sum\n({self.units_str})', f'Put Sum\n({self.units_str})',
            f'Difference\n({self.units_str})', f'Call Boundary\n({self.units_str})',
            f'Put Boundary\n({self.units_str})', 'Call ITM', 'Put ITM']
        self.csv_headers: [str, str, str, str, str, str, str, str, str] = [
            'Time', 'Value', f'Call Sum ({self.units_str})', f'Put Sum ({self.units_str})',
            f'Difference ({self.units_str})',
            f'Call Boundary ({self.units_str})', f'Put Boundary ({self.units_str})', 'Call ITM', 'Put ITM']

        app.layout = html.Div([
            html.H1("NSE-Option-Chain-Analyzer", style={"textAlign": "center"}),
            html.Div([
                html.Label("Mode: "),
                dcc.RadioItems(
                    id='option-mode-btn',
                    options=[
                        {'label': 'Index', 'value': 'Index'},
                        {'label': 'Stock', 'value': 'Stock'}
                    ],
                    value='Index',
                    labelStyle={'display': 'block'}
                )
            ]),
            html.Div([
                html.Label("Index: "),
                dcc.Dropdown(
                    id='index_eq-menu',
                    options=[{'label': index, 'value': index} for index in self.indices],
                    value=self.index,
                    disabled=False
                )
            ]),
            html.Div([
                html.Label("Stock: "),
                dcc.Dropdown(
                    id='stock-menu',
                    options=[{'label': stock, 'value': stock} for stock in self.stocks],
                    value=self.stock,
                    disabled=True
                )
            ]),
            html.Div([
                html.Label("Expiry Date: "),
                dcc.Dropdown(
                    id='date-menu',
                    options=[{'label': date, 'value': date} for date in self.dates],
                    value=self.dates[0],
                    disabled=True
                ),
                html.Button("Refresh", id='date-get', n_clicks=0, style={"margin-left": "10px"})
            ]),
            html.Div([
                html.Label("Strike Price (eg. 14750): "),
                dcc.Input(
                    id='sp-entry',
                    type='text',
                    value='',
                    style={"width": "180px"}
                ),
                html.Button("Start", id='start-btn', n_clicks=0, style={"margin-left": "10px"})
            ]),
            html.Div([
                html.Label("Refresh Interval (in min): "),
                dcc.Dropdown(
                    id='intervals-menu',
                    options=[{'label': str(interval), 'value': interval} for interval in self.intervals],
                    value=self.seconds / 60
                )
            ]),
        ])

        @app.callback(
            Output('symbol-fetch-error', 'children'),
            Output('symbol-fetch-success', 'children'),
        )
        @app.callback(
            Output('stock-menu', 'disabled'),
            Output('index_eq-menu', 'disabled'),
            Output('date-menu', 'disabled'),
            Input('option-mode-btn', 'value')
        )
        def update_mode(option_mode):
            return option_mode == 'Stock', option_mode == 'Index', option_mode == 'Stock'

        @app.callback(
            Output('date-menu', 'options'),
            Input('date-get', 'n_clicks')
        )
        def update_date_options(n_clicks):
            return [{'label': date, 'value': date} for date in self.dates]

        @app.callback(
            Output('date-menu', 'value'),
            Input('date-menu', 'options')
        )
        def update_date_value(available_options):
            if available_options:
                return available_options[0]['value']
            return None

        @app.callback(
            Output('sp-entry', 'value'),
            Input('start-btn', 'n_clicks')
        )
        def reset_sp_entry(n_clicks):
            return ''

    def get_config(self) -> None:
        try:
            self.config_parser.read('NSE-OCA.ini')
            try:
                self.load_nse_icon: bool = self.config_parser.getboolean('main', 'load_nse_icon')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="load_nse_icon")
                self.load_nse_icon: bool = self.config_parser.getboolean('main', 'load_nse_icon')
            try:
                self.index: str = self.config_parser.get('main', 'index_eq')
                if self.index not in self.indices:
                    raise ValueError(f'{self.index} is not a valid index_eq')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="index_eq")
                self.index: str = self.config_parser.get('main', 'index_eq')
            try:
                self.stock: str = self.config_parser.get('main', 'stock')
                if self.stock not in self.stocks:
                    raise ValueError(f'{self.stock} is not a valid stock')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="stock")
                self.stock: str = self.config_parser.get('main', 'stock')
            try:
                self.option_mode: str = self.config_parser.get('main', 'option_mode')
                if self.option_mode not in ('Index', 'Stock'):
                    raise ValueError(f'{self.option_mode} is not a valid option mode')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="option_mode")
                self.option_mode: str = self.config_parser.get('main', 'option_mode')
            try:
                self.seconds: int = self.config_parser.getint('main', 'seconds')
                if self.seconds not in (60, 120, 180, 300, 600, 900):
                    raise ValueError(f'{self.seconds} is not a refresh interval')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="seconds")
                self.seconds: int = self.config_parser.getint('main', 'seconds')
            try:
                self.live_export: bool = self.config_parser.getboolean('main', 'live_export')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="live_export")
                self.live_export: bool = self.config_parser.getboolean('main', 'live_export')
            try:
                self.save_oc: bool = self.config_parser.getboolean('main', 'save_oc')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="save_oc")
                self.save_oc: bool = self.config_parser.getboolean('main', 'save_oc')
            # try:
            #     self.notifications: bool = self.config_parser.getboolean('main', 'notifications') \
            #         if is_windows_10_or_11 else False
            # except (configparser.NoOptionError, ValueError) as err:
            #     print(err, sys.exc_info()[0], "0")
            #     self.create_config(attribute="notifications")
            #     self.notifications: bool = self.config_parser.getboolean('main', 'notifications') \
            #         if is_windows_10_or_11 else False
            try:
                self.auto_stop: bool = self.config_parser.getboolean('main', 'auto_stop')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="auto_stop")
                self.auto_stop: bool = self.config_parser.getboolean('main', 'auto_stop')
            try:
                self.update: bool = self.config_parser.getboolean('main', 'update')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="update")
                self.update: bool = self.config_parser.getboolean('main', 'update')
            try:
                self.logging: bool = self.config_parser.getboolean('main', 'logging')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="logging")
                self.logging: bool = self.config_parser.getboolean('main', 'logging')
            try:
                self.warn_late_update: bool = self.config_parser.getboolean('main', 'warn_late_update')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="warn_late_update")
                self.warn_late_update: bool = self.config_parser.getboolean('main', 'warn_late_update')
        except (configparser.NoSectionError, configparser.MissingSectionHeaderError,
                configparser.DuplicateSectionError, configparser.DuplicateOptionError) as err:
            print(err, sys.exc_info()[0], "0")
            self.create_config(corrupted=True)
            return self.get_config()

    def create_config(self, new: bool = False, corrupted: bool = False, attribute: Optional[str] = None) -> None:
        if new or corrupted:
            if corrupted:
                os.remove('NSE-OCA.ini')
                self.config_parser = configparser.ConfigParser()
            self.config_parser.read('NSE-OCA.ini')
            self.config_parser.add_section('main')
            self.config_parser.set('main', 'load_nse_icon', 'True')
            self.config_parser.set('main', 'index_eq', self.indices[0])
            self.config_parser.set('main', 'stock', self.stocks[0])
            self.config_parser.set('main', 'option_mode', 'Index')
            self.config_parser.set('main', 'seconds', '60')
            self.config_parser.set('main', 'live_export', 'False')
            self.config_parser.set('main', 'save_oc', 'False')
            self.config_parser.set('main', 'notifications', 'False')
            self.config_parser.set('main', 'auto_stop', 'False')
            self.config_parser.set('main', 'update', 'True')
            self.config_parser.set('main', 'logging', 'False')
            self.config_parser.set('main', 'warn_late_update', 'False')
        elif attribute is not None:
            if attribute == "load_nse_icon":
                self.config_parser.set('main', 'load_nse_icon', 'True')
            elif attribute == "index_eq":
                self.config_parser.set('main', 'index_eq', self.indices[0])
            elif attribute == "stock":
                self.config_parser.set('main', 'stock', self.stocks[0])
            elif attribute == "option_mode":
                self.config_parser.set('main', 'option_mode', 'Index')
            elif attribute == "seconds":
                self.config_parser.set('main', 'seconds', '60')
            elif attribute in ("live_export", "save_oc", "notifications", "auto_stop", "logging"):
                self.config_parser.set('main', attribute, 'False')
            elif attribute == "update":
                self.config_parser.set('main', 'update', 'True')
            elif attribute == "warn_late_update":
                self.config_parser.set('main', 'warn_late_update', 'False')

        with open('NSE-OCA.ini', 'w') as f:
            self.config_parser.write(f)


    def get_symbols(self):
        try:
            url_oc = "YOUR_URL_FOR_OPTION_CHAIN"
            url_symbols = "YOUR_URL_FOR_SYMBOLS"
            headers = {"YOUR_HEADERS"}
            session = requests.Session()
            request = session.get(url_oc, headers=headers, timeout=5)
            cookies = dict(request.cookies)
            response = session.get(url_symbols, headers=headers, timeout=5, cookies=cookies)
            response.raise_for_status()
            json_data = response.json()
            indices = [item['symbol'] for item in json_data['data']['IndexList']]
            stocks = [item['symbol'] for item in json_data['data']['UnderlyingList']]
            return None, (indices, stocks)
        except Exception as err:
            print(err)
            return create_error_window(), None
    def get_config(self) -> None:
        try:
            self.config_parser.read('NSE-OCA.ini')
            try:
                self.load_nse_icon: bool = self.config_parser.getboolean('main', 'load_nse_icon')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="load_nse_icon")
                self.load_nse_icon: bool = self.config_parser.getboolean('main', 'load_nse_icon')
            try:
                self.index: str = self.config_parser.get('main', 'index_eq')
                if self.index not in self.indices:
                    raise ValueError(f'{self.index} is not a valid index_eq')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="index_eq")
                self.index: str = self.config_parser.get('main', 'index_eq')
            try:
                self.stock: str = self.config_parser.get('main', 'stock')
                if self.stock not in self.stocks:
                    raise ValueError(f'{self.stock} is not a valid stock')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="stock")
                self.stock: str = self.config_parser.get('main', 'stock')
            try:
                self.option_mode: str = self.config_parser.get('main', 'option_mode')
                if self.option_mode not in ('Index', 'Stock'):
                    raise ValueError(f'{self.option_mode} is not a valid option mode')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="option_mode")
                self.option_mode: str = self.config_parser.get('main', 'option_mode')
            try:
                self.seconds: int = self.config_parser.getint('main', 'seconds')
                if self.seconds not in (60, 120, 180, 300, 600, 900):
                    raise ValueError(f'{self.seconds} is not a refresh interval')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="seconds")
                self.seconds: int = self.config_parser.getint('main', 'seconds')
            try:
                self.live_export: bool = self.config_parser.getboolean('main', 'live_export')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="live_export")
                self.live_export: bool = self.config_parser.getboolean('main', 'live_export')
            try:
                self.save_oc: bool = self.config_parser.getboolean('main', 'save_oc')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="save_oc")
                self.save_oc: bool = self.config_parser.getboolean('main', 'save_oc')
            # try:
            #     self.notifications: bool = self.config_parser.getboolean('main', 'notifications') \
            #         if is_windows_10_or_11 else False
            # except (configparser.NoOptionError, ValueError) as err:
            #     print(err, sys.exc_info()[0], "0")
            #     self.create_config(attribute="notifications")
            #     self.notifications: bool = self.config_parser.getboolean('main', 'notifications') \
            #         if is_windows_10_or_11 else False
            try:
                self.auto_stop: bool = self.config_parser.getboolean('main', 'auto_stop')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="auto_stop")
                self.auto_stop: bool = self.config_parser.getboolean('main', 'auto_stop')
            try:
                self.update: bool = self.config_parser.getboolean('main', 'update')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="update")
                self.update: bool = self.config_parser.getboolean('main', 'update')
            try:
                self.logging: bool = self.config_parser.getboolean('main', 'logging')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="logging")
                self.logging: bool = self.config_parser.getboolean('main', 'logging')
            try:
                self.warn_late_update: bool = self.config_parser.getboolean('main', 'warn_late_update')
            except (configparser.NoOptionError, ValueError) as err:
                print(err, sys.exc_info()[0], "0")
                self.create_config(attribute="warn_late_update")
                self.warn_late_update: bool = self.config_parser.getboolean('main', 'warn_late_update')
        except (configparser.NoSectionError, configparser.MissingSectionHeaderError,
                configparser.DuplicateSectionError, configparser.DuplicateOptionError) as err:
            print(err, sys.exc_info()[0], "0")
            self.create_config(corrupted=True)
            return self.get_config()

    def create_config(self, new: bool = False, corrupted: bool = False, attribute: Optional[str] = None) -> None:
        if new or corrupted:
            if corrupted:
                os.remove('NSE-OCA.ini')
                self.config_parser = configparser.ConfigParser()
            self.config_parser.read('NSE-OCA.ini')
            self.config_parser.add_section('main')
            self.config_parser.set('main', 'load_nse_icon', 'True')
            self.config_parser.set('main', 'index_eq', self.indices[0])
            self.config_parser.set('main', 'stock', self.stocks[0])
            self.config_parser.set('main', 'option_mode', 'Index')
            self.config_parser.set('main', 'seconds', '60')
            self.config_parser.set('main', 'live_export', 'False')
            self.config_parser.set('main', 'save_oc', 'False')
            self.config_parser.set('main', 'notifications', 'False')
            self.config_parser.set('main', 'auto_stop', 'False')
            self.config_parser.set('main', 'update', 'True')
            self.config_parser.set('main', 'logging', 'False')
            self.config_parser.set('main', 'warn_late_update', 'False')
        elif attribute is not None:
            if attribute == "load_nse_icon":
                self.config_parser.set('main', 'load_nse_icon', 'True')
            elif attribute == "index_eq":
                self.config_parser.set('main', 'index_eq', self.indices[0])
            elif attribute == "stock":
                self.config_parser.set('main', 'stock', self.stocks[0])
            elif attribute == "option_mode":
                self.config_parser.set('main', 'option_mode', 'Index')
            elif attribute == "seconds":
                self.config_parser.set('main', 'seconds', '60')
            elif attribute in ("live_export", "save_oc", "notifications", "auto_stop", "logging"):
                self.config_parser.set('main', attribute, 'False')
            elif attribute == "update":
                self.config_parser.set('main', 'update', 'True')
            elif attribute == "warn_late_update":
                self.config_parser.set('main', 'warn_late_update', 'False')

        with open('NSE-OCA.ini', 'w') as f:
            self.config_parser.write(f)

    # noinspection PyUnusedLocal
    def get_data(self) -> Optional[Tuple[Optional[requests.Response], Any]]:
        if self.first_run:
            return self.get_data_first_run()
        else:
            return self.get_data_refresh()

    def get_data_first_run(self) -> Optional[Tuple[Optional[requests.Response], Any]]:
        response: Optional[requests.Response] = None
        self.units_str = 'in K' if self.option_mode == 'Index' else 'in 10s'
        self.output_columns: Tuple[str, str, str, str, str, str, str, str, str] = (
            'Time', 'Value', f'Call Sum\n({self.units_str})', f'Put Sum\n({self.units_str})',
            f'Difference\n({self.units_str})', f'Call Boundary\n({self.units_str})',
            f'Put Boundary\n({self.units_str})', 'Call ITM', 'Put ITM')
        self.csv_headers: Tuple[str, str, str, str, str, str, str, str, str] = (
            'Time', 'Value', f'Call Sum ({self.units_str})', f'Put Sum ({self.units_str})',
            f'Difference ({self.units_str})',
            f'Call Boundary ({self.units_str})', f'Put Boundary ({self.units_str})', 'Call ITM', 'Put ITM')
        self.round_factor: int = 1000 if self.option_mode == 'Index' else 10
        if self.option_mode == 'Index':
            self.index = self.index_var.get()
            self.config_parser.set('main', 'index_eq', f'{self.index}')
        else:
            self.stock = self.stock_var.get()
            self.config_parser.set('main', 'stock', f'{self.stock}')
        with open('NSE-OCA.ini', 'w') as f:
            self.config_parser.write(f)

        url: str = self.url_index + self.index if self.option_mode == 'Index' else self.url_stock + self.stock
        try:
            response = self.session.get(url, headers=self.headers, timeout=5, cookies=self.cookies)
        except Exception as err:
            print(response)
            print(err, sys.exc_info()[0], "1")
            # messagebox.showerror(title="Error", message="Error in fetching dates.\nPlease retry.")
            self.dates.clear()
            self.dates = [""]
            self.date_menu.config(values=tuple(self.dates))
            self.date_menu.current(0)
            return
        json_data: Dict[str, Any]
        if response is not None:
            try:
                json_data = response.json()
            except Exception as err:
                print(response)
                print(err, sys.exc_info()[0], "2")
                json_data = {}
        else:
            json_data = {}
        if json_data == {}:
            # messagebox.showerror(title="Error", message="Error in fetching dates.\nPlease retry.")
            self.dates.clear()
            self.dates = [""]
            try:
                self.date_menu.config(values=tuple(self.dates))
                self.date_menu.current(0)
            except TclError as err:
                print(err, sys.exc_info()[0], "3")
            return
        self.dates.clear()
        for dates in json_data['records']['expiryDates']:
            self.dates.append(dates)
        try:
            self.date_menu.config(values=tuple(self.dates))
            self.date_menu.current(0)
        except TclError:
            pass

        return response, json_data

    def get_data_refresh(self) -> Optional[Tuple[Optional[requests.Response], Any]]:
        request: Optional[requests.Response] = None
        response: Optional[requests.Response] = None
        url: str = self.url_index + self.index if self.option_mode == 'Index' else self.url_stock + self.stock
        try:
            response = self.session.get(url, headers=self.headers, timeout=5, cookies=self.cookies)
            if response.status_code == 401:
                self.session.close()
                self.session = requests.Session()
                request = self.session.get(self.url_oc, headers=self.headers, timeout=5)
                self.cookies = dict(request.cookies)
                response = self.session.get(url, headers=self.headers, timeout=5, cookies=self.cookies)
                print("reset cookies_expired")
        except Exception as err:
            print(request)
            print(response)
            print(err, sys.exc_info()[0], "4")
            try:
                self.session.close()
                self.session = requests.Session()
                request = self.session.get(self.url_oc, headers=self.headers, timeout=5)
                self.cookies = dict(request.cookies)
                response = self.session.get(url, headers=self.headers, timeout=5, cookies=self.cookies)
                print("reset cookies_expired")
            except Exception as err:
                print(request)
                print(response)
                print(err, sys.exc_info()[0], "5")
                return
        if response is not None:
            try:
                json_data: Any = response.json()
            except Exception as err:
                print(response)
                print(err, sys.exc_info()[0], "6")
                json_data = {}
        else:
            json_data = {}
        if json_data == {}:
            return

        return response, json_data



if __name__ == '__main__':
    Nse()
    app.run_server(debug=True)
