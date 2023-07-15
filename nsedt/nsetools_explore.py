from nsetools import Nse
import certifi

cert_path = certifi.where()


def get_all_stock_codes():
    nse = Nse(cert_file=cert_path)
    all_stock_codes = nse.get_stock_codes()
    return all_stock_codes.keys()


stock_codes = get_all_stock_codes()
for code in stock_codes:
    print(code)
