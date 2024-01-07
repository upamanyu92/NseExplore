import json

class JSONNormalizer:
    @staticmethod
    def normalize_json(json_string_with_single_quotes):
        """
        Normalize JSON string by replacing single quotes with double quotes.

        Args:
            json_string_with_single_quotes (str): JSON string with single quotes.

        Returns:
            str: Normalized JSON string with double quotes.
        """
        # Replace single quotes with double quotes
        json_string_with_double_quotes = json_string_with_single_quotes.replace("'", '"')

        return json_string_with_double_quotes

    @staticmethod
    def load_json(json_string):
        """
        Load JSON string into a Python dictionary.

        Args:
            json_string (str): JSON string.

        Returns:
            dict: Parsed JSON data as a dictionary.
        """
        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
