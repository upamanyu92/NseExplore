import requests
from bs4 import BeautifulSoup


def get_stock_codes():
    # Define the NSE URL to retrieve the stock codes
    url = 'https://www1.nseindia.com/content/equities/EQUITY_L.csv'

    # Set headers to mimic a web browser request
    headers = {
        'Referer': 'https://www1.nseindia.com/products/content/equities/equities/archieve_eq.htm',
    }

    # Send GET request to the NSE URL
    response = requests.get(url, headers=headers)

    # Create BeautifulSoup object from the response content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the stock codes from the response
    stock_code = []
    for row in soup.find_all('tr')[1:]:
        cells = row.find_all('td')
        stock_code = cells[0].text.strip()
        stock_code.append(stock_code)

    return stock_code


# Get the list of stock codes
stock_codes = get_stock_codes()

# Print the stock codes
for code in stock_codes:
    print(code)
