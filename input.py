from datetime import date, timedelta
import calendar
import numpy as np
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


def dayahead_sql(resource_id: str, start_date: date, end_date: date) -> str:
    """Build the SQL query for day-ahead prices from start_date to end_date.

    The query selects the "Date", "Delivery Period" and "Price" columns from
    the resource resource_id, for dates from start_date to end_date
    inclusive.
    """
    return (
        f'SELECT "Date", "Delivery Period", "Price" FROM "{resource_id}" '
        f"WHERE \"Date\" >= '{start_date:%Y-%m-%d}' AND \"Date\" <= '{end_date:%Y-%m-%d}'"
    )


def clean_dayahead_prices(rows: list[dict[str, str]]) -> pd.DataFrame:
    """Convert raw day-ahead price rows into typed values.

    Each row must have the keys "Date" (a "YYYY-MM-DD" string), "Delivery
    Period" (start and end times in the form "13:00 - 14:00") and "Price" (a
    number stored as a string).

    Returns a DataFrame with one row per input row, sorted by "start_date",
    and the columns "start_date" and "end_date" (both datetimes combining the
    date with the start and end of the delivery period) and "price" (a
    float). An end time of "00:00" is taken as midnight at the end of the
    day, so "end_date" falls on the following day.

    Raises ValueError if rows is empty, if the start time is not strictly
    before the end time, which includes the ambiguous period "00:00 - 00:00",
    if the price is inf, -inf or nan, if a row does not start where the
    previous row ends (after sorting), or if the rows do not all cover
    periods of the same length.
    """
    if not rows:
        raise ValueError("Rows must not be empty")
    raw = pd.DataFrame(rows)
    required_keys = ["Date", "Delivery Period", "Price"]
    for key in required_keys:
        if key not in raw.columns or raw[key].isna().any():
            raise KeyError(key)

    row_dates = pd.to_datetime(raw["Date"], format="%Y-%m-%d")
    if row_dates.isna().any():
        raise ValueError("Date must not be empty")

    times = raw["Delivery Period"].str.split(" - ")
    if (times.str.len() != 2).any():
        raise ValueError("Delivery Period must contain exactly a start time and an end time")
    start_times = pd.to_datetime(times.str[0], format="%H:%M")
    end_times = pd.to_datetime(times.str[1], format="%H:%M")
    if start_times.isna().any() or end_times.isna().any():
        raise ValueError("Delivery Period start and end times must not be empty")
    start_offsets = start_times - start_times.dt.normalize()
    end_offsets = end_times - end_times.dt.normalize()
    if (start_offsets == end_offsets).any():
        raise ValueError("Delivery Period start time must not equal end time")
    end_offsets = end_offsets.mask(end_offsets == timedelta(0), timedelta(hours=24))
    if (start_offsets > end_offsets).any():
        raise ValueError("Delivery Period start time must not be after end time")

    prices = pd.to_numeric(raw["Price"]).astype("float64")
    if not np.isfinite(prices).all():
        raise ValueError("Price must not be infinite or nan")

    cleaned = pd.DataFrame({
        "start_date": row_dates + start_offsets,
        "end_date": row_dates + end_offsets,
        "price": prices,
    }).sort_values("start_date", ignore_index=True)

    if (cleaned["start_date"].iloc[1:].to_numpy() != cleaned["end_date"].iloc[:-1].to_numpy()).any():
        raise ValueError("Each row must start where the previous row ends")
    if (cleaned["end_date"] - cleaned["start_date"]).nunique() > 1:
        raise ValueError("All rows must cover periods of the same length")
    return cleaned
