from typing import Iterator
from datetime import datetime, timedelta
import requests

class CSVStream:
    def __init__(self, url: str, sep: str = ','):
        self.url = url
        self.sep = sep
        self.__rows, self.column_names, self.encoding = self.__start_stream()

    def __start_stream(self) -> tuple[Iterator[bytes], list[str], str]:
        request = requests.get(self.url, stream=True)
        rows = request.iter_lines()
        first_row = next(rows)
        encoding = request.encoding
        if not encoding:
            raise ValueError("No encoding information available.")
        column_names = first_row.decode(encoding).split(',')
        return rows, column_names, encoding

    def get_next_row(self) -> list[str] | None:
        try:
            row = next(self.__rows)
            return row.decode(self.encoding).split(self.sep)
        except StopIteration:
            return None

def clean_dayahead_price_row(row: list[str], column_names: list[str]) -> dict[str, datetime | float]:
    data = {name: value for name, value in zip(column_names, row)}
    date = datetime.strptime(data["Date"], '%Y-%m-%d')
    times = data["Delivery Period"].split(' - ')
    times = [datetime.strptime(row_time, '%H:%M').time() for row_time in times]
    timedeltas = [timedelta(hours=row_time.hour, minutes=row_time.minute) for row_time in times]
    if timedeltas[1] == timedelta(0):
        timedeltas[1] = timedelta(hours=24)
    dates = [date + row_timedelta for row_timedelta in timedeltas]
    price = float(data['Price'])
    return {"start_date": dates[0], "end_date": dates[1], "price": price}
