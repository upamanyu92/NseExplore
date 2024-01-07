import os
import random
import threading
import time
from urllib.parse import quote

from requests.exceptions import RequestException, HTTPError, ConnectionError

from nsedt.utils import *

# Fetch or renew the cookie
cookies = load_cookie()

# Create a session to manage requests
session = requests.Session()

def fetch_indices(max_retries=3):
    # Fetch indices_to_fetch from the API
    indices_url = "https://www.nseindia.com/api/allIndices"
    for attempt in range(max_retries):
        response = session.get(indices_url, headers=get_headers(), cookies=cookies)
        print(f"indices Response status code: {response.status_code}")

        if response.status_code == 200:
            result_indices = []
            indices_to_fetch = response.json()
            for indexes in indices_to_fetch.get("data"):
                if "index" in indexes:
                    result_indices.append(indexes["index"])

            return result_indices
        elif response.status_code == 403 and "Cookie expired" in response.text:
            # Handle expired cookie by renewing it and retrying the request
            print("Cookie expired. Renewing and retrying...")
            renew_cookie()
            return fetch_indices()
        elif response.status_code == 403 and "Access Restricted" in response.text:
            # Handle access restricted by waiting and retrying the request
            print("Access Restricted. Waiting and retrying...")
            time.sleep(60)
            wait_time = 2 ** attempt + random.uniform(0, 1)
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"Failed to fetch indices_to_fetch. Status Code: {response.status_code}")
            print(response.text)
            return []

def fetch_and_update_data(index_eq, headers_eq, max_retries=3):
    while True:
        fetch_data(index_eq, headers_eq, max_retries)
        time.sleep(600)  # Wait for 10 minutes before fetching again

def fetch_data(index_eq, headers_eq, max_retries=3):
    # Fetch data for a specific index_eq with retry logic
    data_url = f"https://www.nseindia.com/api/equity-stockIndices?index={quote(index_eq)}"
    print(data_url)

    for attempt in range(max_retries):
        try:
            response = session.get(data_url, headers=headers_eq, cookies=cookies)
            response.raise_for_status()  # Raise HTTPError for bad responses

            if response.status_code == 200:
                data = response.json()
                text_filename = f"{index_eq}_output_data.txt"
                with open(os.path.join("data", text_filename), "w") as f:
                    f.write(str(data))

                print(f"Data for {index_eq} has been written to {text_filename}")
                break  # Exit the loop after writing data
            elif response.status_code == 403:  # Rate limit exceeded
                # Implement exponential backoff before retrying
                wait_time = 2 ** attempt + random.uniform(0, 1)
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Unexpected status code: {response.status_code}")
        except (RequestException, HTTPError, ConnectionError) as e:
            print(f"Error: {e}")

        # Retry after a delay
        print(f"Retrying {attempt + 1}/{max_retries}...")
        time.sleep(1)  # Add a delay before retrying

    print(f"Failed to retrieve data for {index_eq} after {max_retries} attempts.")

# Fetch indices
indices = fetch_indices()

# Create threads for each index_eq
threads = []
for index in indices:
    thread = threading.Thread(target=fetch_and_update_data, args=(index, get_headers()))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish (not really needed in this continuous setup)
for thread in threads:
    thread.join()

# This code will keep running continuously as the threads are in an infinite loop