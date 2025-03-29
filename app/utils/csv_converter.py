import csv
from io import StringIO
import json


def to_json(data, config=None):
    """
    Convert CSV data to JSON format

    Args:
        data: CSV data as a string
        config: Optional configuration dictionary containing:
               - delimiter: CSV delimiter (default ',')
               - fields: List of fields to force specific field names
               - array: Boolean to force array output even for single row (default False)
    """
    # Get configuration options
    config = config or {}
    delimiter = config.get("delimiter", ",")
    force_array = config.get("array", False)

    # Create CSV reader from string input
    input_file = StringIO(data)
    reader = csv.DictReader(input_file, delimiter=delimiter)

    # If fields are specified in config, override the fieldnames
    if "fields" in config:
        reader.fieldnames = config["fields"]

    # Convert CSV rows to list of dictionaries
    result = list(reader)

    # If there's only one row and force_array is False, return just the object
    if len(result) == 1 and not force_array:
        return json.dumps(result[0])

    return json.dumps(result)
