import datetime
import pytest
from input import month_ranges, clean_dayahead_price_row

d = datetime.date
dt = datetime.datetime


def month(label: str, start_date: datetime.date, end_date: datetime.date) -> dict:
    return {"label": label, "start_date": start_date, "end_date": end_date}


def raw_row(row_date: str = "2024-03-15", delivery_period: str = "13:00 - 14:00", price: str = "45.67") -> dict:
    return {"Date": row_date, "Delivery Period": delivery_period, "Price": price}


def clean_row(start_date: datetime.datetime, end_date: datetime.datetime, price: float) -> dict:
    return {"start_date": start_date, "end_date": end_date, "price": price}


class TestMonthRanges:
    class TestRangeWithinSingleMonth:
        def test_returns_single_entry_when_range_is_whole_month(self):
            assert month_ranges(d(2024, 4, 1), d(2024, 4, 30)) == [
                month("2024-04", d(2024, 4, 1), d(2024, 4, 30)),
            ]

        def test_returns_single_entry_when_start_on_first_day_and_end_mid_month(self):
            assert month_ranges(d(2024, 3, 1), d(2024, 3, 20)) == [
                month("2024-03", d(2024, 3, 1), d(2024, 3, 20)),
            ]

        def test_returns_single_entry_when_start_mid_month_and_end_on_last_day(self):
            assert month_ranges(d(2024, 3, 5), d(2024, 3, 31)) == [
                month("2024-03", d(2024, 3, 5), d(2024, 3, 31)),
            ]

        def test_returns_single_entry_when_both_dates_mid_month(self):
            assert month_ranges(d(2024, 2, 5), d(2024, 2, 20)) == [
                month("2024-02", d(2024, 2, 5), d(2024, 2, 20)),
            ]

        def test_returns_single_day_entry_when_start_equals_end(self):
            assert month_ranges(d(2024, 5, 17), d(2024, 5, 17)) == [
                month("2024-05", d(2024, 5, 17), d(2024, 5, 17)),
            ]

    class TestRangeAcrossMonths:
        def test_returns_unclipped_entries_when_start_on_first_day_and_end_on_last_day(self):
            assert month_ranges(d(2024, 3, 1), d(2024, 5, 31)) == [
                month("2024-03", d(2024, 3, 1), d(2024, 3, 31)),
                month("2024-04", d(2024, 4, 1), d(2024, 4, 30)),
                month("2024-05", d(2024, 5, 1), d(2024, 5, 31)),
            ]

        def test_clips_final_entry_when_start_on_first_day_and_end_mid_month(self):
            assert month_ranges(d(2024, 3, 1), d(2024, 5, 15)) == [
                month("2024-03", d(2024, 3, 1), d(2024, 3, 31)),
                month("2024-04", d(2024, 4, 1), d(2024, 4, 30)),
                month("2024-05", d(2024, 5, 1), d(2024, 5, 15)),
            ]

        def test_clips_first_entry_when_start_mid_month_and_end_on_last_day(self):
            assert month_ranges(d(2024, 3, 10), d(2024, 5, 31)) == [
                month("2024-03", d(2024, 3, 10), d(2024, 3, 31)),
                month("2024-04", d(2024, 4, 1), d(2024, 4, 30)),
                month("2024-05", d(2024, 5, 1), d(2024, 5, 31)),
            ]

        def test_clips_first_and_final_entries_when_both_dates_mid_month(self):
            assert month_ranges(d(2024, 3, 10), d(2024, 5, 15)) == [
                month("2024-03", d(2024, 3, 10), d(2024, 3, 31)),
                month("2024-04", d(2024, 4, 1), d(2024, 4, 30)),
                month("2024-05", d(2024, 5, 1), d(2024, 5, 15)),
            ]

    class TestStartOnLastDayOfMonth:
        def test_returns_first_entry_single_day_when_start_on_last_day_and_end_mid_month(self):
            assert month_ranges(d(2024, 3, 31), d(2024, 5, 15)) == [
                month("2024-03", d(2024, 3, 31), d(2024, 3, 31)),
                month("2024-04", d(2024, 4, 1), d(2024, 4, 30)),
                month("2024-05", d(2024, 5, 1), d(2024, 5, 15)),
            ]

        def test_returns_single_day_entry_when_start_equals_end_on_last_day(self):
            assert month_ranges(d(2024, 6, 30), d(2024, 6, 30)) == [
                month("2024-06", d(2024, 6, 30), d(2024, 6, 30)),
            ]

    class TestEndOnFirstDayOfMonth:
        def test_returns_last_entry_single_day_when_start_mid_month_and_end_on_first_day(self):
            assert month_ranges(d(2024, 3, 10), d(2024, 5, 1)) == [
                month("2024-03", d(2024, 3, 10), d(2024, 3, 31)),
                month("2024-04", d(2024, 4, 1), d(2024, 4, 30)),
                month("2024-05", d(2024, 5, 1), d(2024, 5, 1)),
            ]

        def test_returns_single_day_entry_when_start_equals_end_on_first_day(self):
            assert month_ranges(d(2024, 7, 1), d(2024, 7, 1)) == [
                month("2024-07", d(2024, 7, 1), d(2024, 7, 1)),
            ]

    class TestStartOnLastDayOfMonthAndEndOnFirstDayOfMonth:
        def test_returns_two_single_day_entries_when_start_on_last_day_and_end_on_first_day_one_day_later(self):
            assert month_ranges(d(2024, 3, 31), d(2024, 4, 1)) == [
                month("2024-03", d(2024, 3, 31), d(2024, 3, 31)),
                month("2024-04", d(2024, 4, 1), d(2024, 4, 1)),
            ]

        def test_returns_first_and_last_entry_single_day_when_start_on_last_day_and_end_on_first_day_more_than_one_day_later(self):
            assert month_ranges(d(2024, 1, 31), d(2024, 3, 1)) == [
                month("2024-01", d(2024, 1, 31), d(2024, 1, 31)),
                month("2024-02", d(2024, 2, 1), d(2024, 2, 29)),
                month("2024-03", d(2024, 3, 1), d(2024, 3, 1)),
            ]

    class TestRangeAcrossYears:
        def test_returns_one_entry_per_month_across_two_years(self):
            assert month_ranges(d(2023, 11, 15), d(2024, 2, 10)) == [
                month("2023-11", d(2023, 11, 15), d(2023, 11, 30)),
                month("2023-12", d(2023, 12, 1), d(2023, 12, 31)),
                month("2024-01", d(2024, 1, 1), d(2024, 1, 31)),
                month("2024-02", d(2024, 2, 1), d(2024, 2, 10)),
            ]

        def test_returns_one_unique_entry_per_month_across_many_years(self):
            result = month_ranges(d(2021, 6, 20), d(2024, 3, 5))
            assert len(result) == 34

        def test_returns_single_day_entries_for_adjacent_days_at_year_boundary(self):
            assert month_ranges(d(2023, 12, 31), d(2024, 1, 1)) == [
                month("2023-12", d(2023, 12, 31), d(2023, 12, 31)),
                month("2024-01", d(2024, 1, 1), d(2024, 1, 1)),
            ]

    class TestMonthLengths:
        @pytest.mark.parametrize(
            "year, last_day",
            [
                pytest.param(2023, 28, id="common_year"),
                pytest.param(2024, 29, id="leap_year"),
                pytest.param(2100, 28, id="century_not_leap"),
                pytest.param(2000, 29, id="century_leap"),
            ],
        )
        def test_ends_february_on_correct_day_for_year_type(self, year: int, last_day: int):
            assert month_ranges(d(year, 2, 1), d(year, 2, last_day)) == [
                month(f"{year}-02", d(year, 2, 1), d(year, 2, last_day)),
            ]

        def test_includes_leap_day_in_leap_year_when_range_extends_into_march(self):
            assert month_ranges(d(2024, 2, 1), d(2024, 3, 31)) == [
                month("2024-02", d(2024, 2, 1), d(2024, 2, 29)),
                month("2024-03", d(2024, 3, 1), d(2024, 3, 31)),
            ]

        def test_excludes_leap_day_in_common_year_between_clipped_months(self):
            assert month_ranges(d(2023, 1, 31), d(2023, 3, 1)) == [
                month("2023-01", d(2023, 1, 31), d(2023, 1, 31)),
                month("2023-02", d(2023, 2, 1), d(2023, 2, 28)),
                month("2023-03", d(2023, 3, 1), d(2023, 3, 1)),
            ]

        def test_returns_correct_lengths_for_every_month_in_a_year(self):
            result = month_ranges(d(2023, 1, 1), d(2023, 12, 31))
            assert [entry["end_date"].day for entry in result] == [
                31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31,
            ]

    class TestInvalidInput:
        @pytest.mark.parametrize(
            "start_date, end_date",
            [
                pytest.param(d(2024, 3, 2), d(2024, 3, 1), id="same_month"),
                pytest.param(d(2024, 2, 1), d(2024, 1, 31), id="adjacent_months"),
                pytest.param(d(2025, 1, 1), d(2023, 12, 31), id="different_years"),
            ],
        )
        def test_raises_value_error_when_start_after_end(self, start_date, end_date):
            with pytest.raises(ValueError):
                month_ranges(start_date, end_date)


class TestCleanDayaheadPriceRow:
    class TestDeliveryPeriodPosition:
        def test_returns_start_at_midnight_when_period_starts_at_beginning_of_day(self):
            assert clean_dayahead_price_row(raw_row("2024-03-15", "00:00 - 01:00", "45.67")) == clean_row(
                dt(2024, 3, 15, 0, 0), dt(2024, 3, 15, 1, 0), 45.67,
            )

        def test_returns_end_at_midnight_of_following_day_when_period_ends_at_end_of_day(self):
            assert clean_dayahead_price_row(raw_row("2024-03-15", "23:00 - 00:00", "45.67")) == clean_row(
                dt(2024, 3, 15, 23, 0), dt(2024, 3, 16, 0, 0), 45.67,
            )

        def test_returns_start_and_end_on_same_day_when_period_starts_and_ends_mid_day(self):
            assert clean_dayahead_price_row(raw_row("2024-03-15", "13:00 - 14:00", "45.67")) == clean_row(
                dt(2024, 3, 15, 13, 0), dt(2024, 3, 15, 14, 0), 45.67,
            )

    class TestStartBeforeEnd:
        @pytest.mark.parametrize(
            "delivery_period",
            [
                pytest.param("14:00 - 13:00", id="start_after_end"),
                pytest.param("13:00 - 13:00", id="start_equals_end"),
            ],
        )
        def test_raises_value_error_when_start_not_strictly_before_end(self, delivery_period: str):
            with pytest.raises(ValueError):
                clean_dayahead_price_row(raw_row(delivery_period=delivery_period))

        def test_raises_value_error_when_period_starts_and_ends_at_midnight(self):
            with pytest.raises(ValueError):
                clean_dayahead_price_row(raw_row(delivery_period="00:00 - 00:00"))

    class TestInvalidInput:
        @pytest.mark.parametrize("missing_key", ["Date", "Delivery Period", "Price"])
        def test_raises_key_error_when_required_key_missing(self, missing_key: str):
            row = raw_row()
            del row[missing_key]
            with pytest.raises(KeyError):
                clean_dayahead_price_row(row)

        @pytest.mark.parametrize(
            "row_date",
            [
                pytest.param("15/03/2024", id="day_first_with_slashes"),
                pytest.param("2024-03-15 00:00", id="includes_time"),
                pytest.param("2024-02-30", id="day_not_in_month"),
                pytest.param("", id="empty"),
            ],
        )
        def test_raises_value_error_when_date_has_incorrect_format(self, row_date: str):
            with pytest.raises(ValueError):
                clean_dayahead_price_row(raw_row(row_date=row_date))

        @pytest.mark.parametrize(
            "delivery_period",
            [
                pytest.param("13:00-14:00", id="no_spaces_around_separator"),
                pytest.param("13:00 to 14:00", id="wrong_separator"),
                pytest.param("1pm - 2pm", id="twelve_hour_clock"),
                pytest.param("13:00 - 25:00", id="hour_out_of_range"),
                pytest.param("13:00", id="single_time"),
                pytest.param("13:00 - 14:00 - 15:00", id="three_times"),
                pytest.param("", id="empty"),
            ],
        )
        def test_raises_value_error_when_delivery_period_has_incorrect_format(self, delivery_period: str):
            with pytest.raises(ValueError):
                clean_dayahead_price_row(raw_row(delivery_period=delivery_period))

        @pytest.mark.parametrize(
            "price",
            [
                pytest.param("abc", id="not_a_number"),
                pytest.param("45,67", id="comma_decimal_separator"),
                pytest.param("£45.67", id="currency_symbol"),
                pytest.param("", id="empty"),
            ],
        )
        def test_raises_value_error_when_price_has_incorrect_format(self, price: str):
            with pytest.raises(ValueError):
                clean_dayahead_price_row(raw_row(price=price))
