from app.utils import json_converter, csv_converter, excel_converter


class TransformationService:
    def transform(self, source_format, target_format, data, config=None):
        """
        Transform data from source format to target format using provided config

        Args:
            source_format: The input format (json, csv, excel)
            target_format: The output format (json, csv, excel)
            data: The input data to transform
            config: Optional configuration for the transformation
                   (field mappings, options, etc.)
        """
        # Select the appropriate transformation method based on formats
        if source_format == "json" and target_format == "csv":
            return json_converter.to_csv(data, config)
        elif source_format == "csv" and target_format == "json":
            return csv_converter.to_json(data, config)
        # Pending implementation
        elif source_format == "json" and target_format == "excel":
            return excel_converter.from_json(data, config)
        elif source_format == "csv" and target_format == "excel":
            return excel_converter.from_csv(data, config)
        elif source_format == "excel" and target_format == "json":
            return excel_converter.to_json(data, config)
        elif source_format == "excel" and target_format == "csv":
            return excel_converter.to_csv(data, config)
        else:
            raise ValueError(
                f"Unsupported transformation: {source_format} to {target_format}"
            )
