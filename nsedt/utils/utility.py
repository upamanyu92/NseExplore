import locale
from babel.numbers import format_currency


def remove_null_values(json_obj):
    if isinstance(json_obj, list):
        return [remove_null_values(item) for item in json_obj if item is not None]
    elif isinstance(json_obj, dict):
        return {key: remove_null_values(value) for key, value in json_obj.items() if value is not None}
    else:
        return json_obj


def get_inr(number):
    return format_currency(float(number), 'INR', locale='en_IN')
