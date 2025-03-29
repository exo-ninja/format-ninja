import json
import csv
from io import StringIO


def to_csv(data, config=None):
    """
    Convert JSON data to CSV format

    Args:
        data: JSON data (either a string or parsed JSON object)
        config: Optional configuration dictionary containing:
               - fields: List of fields to include in CSV
               - delimiter: CSV delimiter (default ',')
               - headers: Boolean to include headers (default True)
    """
    # Parse JSON if it's a string
    if isinstance(data, str):
        data = json.loads(data)

    # Ensure data is a list of dictionaries
    if not isinstance(data, list):
        data = [data]

    # Get configuration options
    config = config or {}
    delimiter = config.get("delimiter", ",")
    include_headers = config.get("headers", True)

    # If fields are specified in config, use those
    # Otherwise, get all unique fields from the data
    if "fields" in config:
        fieldnames = config["fields"]
    else:
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))

    # Create string buffer for CSV output
    output = StringIO()
    writer = csv.DictWriter(
        output, fieldnames=fieldnames, delimiter=delimiter, extrasaction="ignore"
    )

    # Write headers if configured
    if include_headers:
        writer.writeheader()

    # Write data rows
    writer.writerows(data)

    return output.getvalue()
