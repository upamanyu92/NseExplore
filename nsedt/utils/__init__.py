"""
utils for nsedt
"""

import json
import os
from datetime import datetime

import pandas as pd
import requests
from nsedt.resources import constants as cns


def get_headers():
    """
    Args:
       ---
    Returns:
        Json: json containing nse header
    """

    return {
        "Host": "www.nseindia.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Connection": "keep-alive",
    }


def get_cookies():
    """
    Args:
       ---
    Returns:
        Json: json containing nse cookies_expired
    """

    response = requests.get(cns.BASE_URL, timeout=30, headers=get_headers())
    try:
        cookies = response.cookies.get_dict()
        print("Cookie has been fetched.")
        with open("cookie.json", "w") as cookie_file:
            json.dump(cookies, cookie_file)
    except AttributeError:
        if response.status_code != 200:
            try:
                os.remove("cookie.json")
                print(f"File 'cookie.json' deleted successfully.")
            except FileNotFoundError:
                print(f"File 'cookie.json' not found.")
            except Exception as e:
                print(f"Error deleting file 'cookie.json': {e}")
            raise ValueError("Retry again in a minute.")
        else:
            set_cookie_header = response.headers.get("Set-Cookie")
            if set_cookie_header:
                cookies = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in set_cookie_header.split("; ")}

                # Store the cookie in a file
                with open("cookie.json", "w") as cookie_file:
                    json.dump(cookies, cookie_file)
            print("Cookie has been fetched and stored.")
    return response.cookies.get_dict()


def load_cookie():
    try:
        # Load the cookie from the file
        with open("cookie.json", "r") as cookie_file:
            cookies_to_load = json.load(cookie_file)
        return cookies_to_load
    except FileNotFoundError:
        print("Cookie file not found. Fetching a new cookie.")
        get_cookies()
        return load_cookie()

def is_cookie_expired(cookies_expired):
    expiration_time_str = cookies_expired.get("expires", "")

    if expiration_time_str:
        expiration_time = datetime.strptime(expiration_time_str, "%a, %d %b %Y %H:%M:%S %Z")
        now = datetime.utcnow()
        return now > expiration_time
    else:
        return False

def renew_cookie():
    print("Renewing cookie...")
    get_cookies()



def fetch_url(url, cookies, key=None, response_type="panda_df"):
    """
    Args:
       url (str): URL to fetch
       cookies (str): NSE cokies
       key (str, Optional):
    Returns:
        Pandas DataFrame: df containing url data

    """

    response = requests.get(
        url=url,
        timeout=30,
        headers=get_headers(),
        cookies=cookies,
    )

    if response.status_code == 200:
        json_response = json.loads(response.content)

        if response_type != "panda_df":
            return json_response
        if key is None:
            return pd.DataFrame.from_dict(json_response)

        return pd.DataFrame.from_dict(json_response[key])

    raise ValueError("Please try again in a minute.")
