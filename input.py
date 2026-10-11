from datetime import datetime, date, timedelta
import calendar

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


def clean_dayahead_price_row(row: dict[str, str]) -> dict[str, datetime | float]:
    row_date = datetime.strptime(row["Date"], '%Y-%m-%d')
    times = row["Delivery Period"].split(' - ')
    times = [datetime.strptime(row_time, '%H:%M').time() for row_time in times]
    timedeltas = [timedelta(hours=row_time.hour, minutes=row_time.minute) for row_time in times]
    if timedeltas[1] == timedelta(0):
        timedeltas[1] = timedelta(hours=24)
    dates = [row_date + row_timedelta for row_timedelta in timedeltas]
    price = float(row['Price'])
    return {"start_date": dates[0], "end_date": dates[1], "price": price}
