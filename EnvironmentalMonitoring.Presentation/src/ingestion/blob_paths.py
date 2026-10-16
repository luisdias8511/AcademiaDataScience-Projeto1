from datetime import datetime


class BlobPaths:
    @staticmethod
    def build_blob_reading_name(
        station_code: str,
        reading_datetime: str | datetime
    ) -> str:
        if isinstance(reading_datetime, str):
            reading_datetime = datetime.fromisoformat(reading_datetime)

        return (
            f"year={reading_datetime:%Y}/"
            f"month={reading_datetime:%m}/"
            f"day={reading_datetime:%d}/"
            f"station={station_code}/"
            f"{reading_datetime:%Y%m%dT%H%M%SZ}.json"
        )