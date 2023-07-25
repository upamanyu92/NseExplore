from nsedt import equity as eq
from datetime import date

start_date = date(2022, 1, 1)
end_date = date(2023, 1, 10)
print(eq.get_price(start_date, end_date, symbol="TCS"))
# start_date = "01-05-2023"
# end_date = "03-05-2023"
print(eq.get_corpinfo(start_date, end_date, symbol="TCS"))
# print(eq.get_event(start_date, end_date))
# print(eq.get_event())
print(eq.get_marketstatus())
# print(eq.get_marketstatus(response_type="json"))
# print(eq.get_companyinfo(symbol="TCS"))
# print(eq.get_companyinfo(symbol="TCS", response_type="json"))
# print(eq.get_chartdata(symbol="TCS"))
