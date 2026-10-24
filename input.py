from datetime import datetime, date, timedelta
import calendar
import math
import pandas as pd

def month_ranges(start_date: date, end_date: date) -> list[dict[str, str | date]]:
    """Split the period start_date..end_date (inclusive) into calendar months.

    Returns a list in chronological order with one dict per month. Each dict has
    the keys "label" (a "YYYY-MM" string), "start_date" and "end_date" (both
    datetime.date objects). The first month starts at start_date and the last
    month ends at end_date; every other month covers the full calendar month.
    """
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    result = []
    year, month = start_date.year, start_date.month

    while (year, month) <= (end_date.year, end_date.month):
        first = date(year, month, 1)
        last = date(year, month, calendar.monthrange(year, month)[1])

        result.append({
            "label": f"{year}-{month:02d}",
            "start_date": max(first, start_date),
            "end_date": min(last, end_date),
        })

        month += 1
        if month > 12:
            month = 1
            year += 1

    return result


def clean_dayahead_prices(rows: list[dict[str, str]]) -> pd.DataFrame:
    """Convert raw day-ahead price rows into typed values.

    Each row must have the keys "Date" (a "YYYY-MM-DD" string), "Delivery
    Period" (start and end times in the form "13:00 - 14:00") and "Price" (a
    number stored as a string).

    Returns a DataFrame with one row per input row, sorted by "start_date", and
    the columns "start_date" and "end_date" (both datetimes combining the date
    with the start and end of the delivery period) and "price" (a float). An end
    time of "00:00" is taken as midnight at the end of the day, so "end_date"
    falls on the following day.

    Raises ValueError if rows is empty, if the start time is not strictly
    before the end time, which includes the ambiguous period "00:00 - 00:00",
    if the price is inf, -inf or nan, if a row does not start where the
    previous row ends, or if the rows do not all cover periods of the same
    length.
    """
    if not rows:
        raise ValueError("Rows must not be empty")
    cleaned_rows = []
    for row in rows:
        row_date = datetime.strptime(row["Date"], '%Y-%m-%d')
        times = row["Delivery Period"].split(' - ')
        if len(times) != 2:
            raise ValueError("Delivery Period must contain exactly a start time and an end time")
        times = [datetime.strptime(row_time, '%H:%M').time() for row_time in times]
        timedeltas = [timedelta(hours=row_time.hour, minutes=row_time.minute) for row_time in times]
        if timedeltas[0] == timedeltas[1]:
            raise ValueError("Delivery Period start time must not equal end time")
        if timedeltas[1] == timedelta(0):
            timedeltas[1] = timedelta(hours=24)
        if timedeltas[0] > timedeltas[1]:
            raise ValueError("Delivery Period start time must not be after end time")
        dates = [row_date + row_timedelta for row_timedelta in timedeltas]
        price = float(row['Price'])
        if not math.isfinite(price):
            raise ValueError("Price must not be infinite or nan")
        cleaned_rows.append({"start_date": dates[0], "end_date": dates[1], "price": price})
    cleaned_rows.sort(key=lambda cleaned_row: cleaned_row["start_date"])
    for previous_row, current_row in zip(cleaned_rows, cleaned_rows[1:]):
        if current_row["start_date"] != previous_row["end_date"]:
            raise ValueError("Each row must start where the previous row ends")
        if current_row["end_date"] - current_row["start_date"] != previous_row["end_date"] - previous_row["start_date"]:
            raise ValueError("All rows must cover periods of the same length")
    return pd.DataFrame(cleaned_rows)
