import datetime
import pandas as pd
import pytest
from input import month_ranges, clean_dayahead_prices, dayahead_sql

d = datetime.date
dt = datetime.datetime


def month(label: str, start_date: datetime.date, end_date: datetime.date) -> dict:
    return {"label": label, "start_date": start_date, "end_date": end_date}


def raw_row(row_date: str, delivery_period: str, price: str) -> dict:
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


class TestCleanDayaheadPrices:
    class TestSingleRow:
        def test_returns_start_at_midnight_when_period_starts_at_beginning_of_day(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([raw_row("2024-03-15", "00:00 - 01:00", "45.67")]),
                pd.DataFrame([clean_row(dt(2024, 3, 15, 0, 0), dt(2024, 3, 15, 1, 0), 45.67)]),
            )

        def test_returns_end_at_midnight_of_following_day_when_period_ends_at_end_of_day(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([raw_row("2024-03-15", "23:00 - 00:00", "45.67")]),
                pd.DataFrame([clean_row(dt(2024, 3, 15, 23, 0), dt(2024, 3, 16, 0, 0), 45.67)]),
            )

        def test_returns_start_and_end_on_same_day_when_period_starts_and_ends_mid_day(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([raw_row("2024-03-15", "13:00 - 14:00", "45.67")]),
                pd.DataFrame([clean_row(dt(2024, 3, 15, 13, 0), dt(2024, 3, 15, 14, 0), 45.67)]),
            )

        @pytest.mark.parametrize(
            "delivery_period",
            [
                pytest.param("14:00 - 13:00", id="start_after_end"),
                pytest.param("13:00 - 13:00", id="start_equals_end"),
            ],
        )
        def test_raises_value_error_when_start_not_strictly_before_end(self, delivery_period: str):
            with pytest.raises(ValueError):
                clean_dayahead_prices([raw_row("2024-01-08", delivery_period, "12.34")])

        def test_raises_value_error_when_period_starts_and_ends_at_midnight(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([raw_row("2024-02-19", "00:00 - 00:00", "56.78")])

    class TestMultipleRows:
        def test_returns_cleaned_rows_when_start_at_midnight_and_end_at_midnight(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([
                    raw_row("2024-03-15", "00:00 - 06:00", "10.5"),
                    raw_row("2024-03-15", "06:00 - 12:00", "20.5"),
                    raw_row("2024-03-15", "12:00 - 18:00", "30.5"),
                    raw_row("2024-03-15", "18:00 - 00:00", "40.5"),
                    raw_row("2024-03-16", "00:00 - 06:00", "50.5"),
                    raw_row("2024-03-16", "06:00 - 12:00", "60.5"),
                    raw_row("2024-03-16", "12:00 - 18:00", "70.5"),
                    raw_row("2024-03-16", "18:00 - 00:00", "80.5"),
                ]),
                pd.DataFrame([
                    clean_row(dt(2024, 3, 15, 0, 0), dt(2024, 3, 15, 6, 0), 10.5),
                    clean_row(dt(2024, 3, 15, 6, 0), dt(2024, 3, 15, 12, 0), 20.5),
                    clean_row(dt(2024, 3, 15, 12, 0), dt(2024, 3, 15, 18, 0), 30.5),
                    clean_row(dt(2024, 3, 15, 18, 0), dt(2024, 3, 16, 0, 0), 40.5),
                    clean_row(dt(2024, 3, 16, 0, 0), dt(2024, 3, 16, 6, 0), 50.5),
                    clean_row(dt(2024, 3, 16, 6, 0), dt(2024, 3, 16, 12, 0), 60.5),
                    clean_row(dt(2024, 3, 16, 12, 0), dt(2024, 3, 16, 18, 0), 70.5),
                    clean_row(dt(2024, 3, 16, 18, 0), dt(2024, 3, 17, 0, 0), 80.5),
                ]),
            )

        def test_returns_cleaned_rows_when_start_at_midnight_and_end_not_at_midnight(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([
                    raw_row("2024-03-15", "00:00 - 06:00", "10.5"),
                    raw_row("2024-03-15", "06:00 - 12:00", "20.5"),
                    raw_row("2024-03-15", "12:00 - 18:00", "30.5"),
                    raw_row("2024-03-15", "18:00 - 00:00", "40.5"),
                    raw_row("2024-03-16", "00:00 - 06:00", "50.5"),
                    raw_row("2024-03-16", "06:00 - 12:00", "60.5"),
                ]),
                pd.DataFrame([
                    clean_row(dt(2024, 3, 15, 0, 0), dt(2024, 3, 15, 6, 0), 10.5),
                    clean_row(dt(2024, 3, 15, 6, 0), dt(2024, 3, 15, 12, 0), 20.5),
                    clean_row(dt(2024, 3, 15, 12, 0), dt(2024, 3, 15, 18, 0), 30.5),
                    clean_row(dt(2024, 3, 15, 18, 0), dt(2024, 3, 16, 0, 0), 40.5),
                    clean_row(dt(2024, 3, 16, 0, 0), dt(2024, 3, 16, 6, 0), 50.5),
                    clean_row(dt(2024, 3, 16, 6, 0), dt(2024, 3, 16, 12, 0), 60.5),
                ]),
            )

        def test_returns_cleaned_rows_when_start_not_at_midnight_and_end_at_midnight(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([
                    raw_row("2024-03-15", "12:00 - 18:00", "30.5"),
                    raw_row("2024-03-15", "18:00 - 00:00", "40.5"),
                ]),
                pd.DataFrame([
                    clean_row(dt(2024, 3, 15, 12, 0), dt(2024, 3, 15, 18, 0), 30.5),
                    clean_row(dt(2024, 3, 15, 18, 0), dt(2024, 3, 16, 0, 0), 40.5),
                ]),
            )

        def test_returns_cleaned_rows_when_start_not_at_midnight_and_end_not_at_midnight(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([
                    raw_row("2024-03-15", "06:00 - 12:00", "20.5"),
                    raw_row("2024-03-15", "12:00 - 18:00", "30.5"),
                ]),
                pd.DataFrame([
                    clean_row(dt(2024, 3, 15, 6, 0), dt(2024, 3, 15, 12, 0), 20.5),
                    clean_row(dt(2024, 3, 15, 12, 0), dt(2024, 3, 15, 18, 0), 30.5),
                ]),
            )

        def test_returns_cleaned_rows_sorted_by_start_when_rows_out_of_order(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([
                    raw_row("2025-01-01", "00:00 - 06:00", "84.6"),
                    raw_row("2024-12-31", "12:00 - 18:00", "95.15"),
                    raw_row("2025-01-01", "06:00 - 12:00", "78.3"),
                    raw_row("2024-12-31", "18:00 - 00:00", "102.4"),
                ]),
                pd.DataFrame([
                    clean_row(dt(2024, 12, 31, 12, 0), dt(2024, 12, 31, 18, 0), 95.15),
                    clean_row(dt(2024, 12, 31, 18, 0), dt(2025, 1, 1, 0, 0), 102.4),
                    clean_row(dt(2025, 1, 1, 0, 0), dt(2025, 1, 1, 6, 0), 84.6),
                    clean_row(dt(2025, 1, 1, 6, 0), dt(2025, 1, 1, 12, 0), 78.3),
                ]),
            )

    class TestIgnoreIrrelevantExtras:
        def test_ignores_keys_other_than_required_keys(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([
                    {"Date": "2024-11-11", "Delivery Period": "09:00 - 10:00", "Price": "74.2", "_id": "1", "Currency": "GBP"},
                    {"Date": "2024-11-11", "Delivery Period": "10:00 - 11:00", "Price": "71.85", "_id": "2", "Currency": "GBP"},
                ]),
                pd.DataFrame([
                    clean_row(dt(2024, 11, 11, 9, 0), dt(2024, 11, 11, 10, 0), 74.2),
                    clean_row(dt(2024, 11, 11, 10, 0), dt(2024, 11, 11, 11, 0), 71.85),
                ]),
            )

        def test_ignores_trailing_zeros_in_price(self):
            pd.testing.assert_frame_equal(
                clean_dayahead_prices([
                    raw_row("2025-06-08", "14:00 - 15:00", "46.470000"),
                    raw_row("2025-06-08", "15:00 - 16:00", "52.100000"),
                ]),
                pd.DataFrame([
                    clean_row(dt(2025, 6, 8, 14, 0), dt(2025, 6, 8, 15, 0), 46.47),
                    clean_row(dt(2025, 6, 8, 15, 0), dt(2025, 6, 8, 16, 0), 52.1),
                ]),
            )

    class TestStartEqualToPreviousEnd:
        def test_raises_value_error_when_gap_between_rows(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-06-10", "00:00 - 00:30", "41.2"),
                    raw_row("2024-06-10", "01:00 - 01:30", "39.75"),
                    raw_row("2024-06-10", "02:00 - 02:30", "38.6"),
                ])

        def test_raises_value_error_when_rows_overlap(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-06-10", "03:00 - 04:00", "37.9"),
                    raw_row("2024-06-10", "03:30 - 04:30", "36.45"),
                    raw_row("2024-06-10", "04:30 - 05:30", "35.8"),
                ])

        def test_raises_value_error_when_rows_duplicated(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-06-10", "10:00 - 11:00", "63.4"),
                    raw_row("2024-06-10", "10:00 - 11:00", "63.4"),
                    raw_row("2024-06-10", "11:00 - 12:00", "61.95"),
                ])

    class TestRowsHaveSameLength:
        def test_raises_value_error_when_first_row_longer(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-08-14", "00:00 - 02:00", "29.4"),
                    raw_row("2024-08-14", "02:00 - 03:00", "27.85"),
                    raw_row("2024-08-14", "03:00 - 04:00", "26.3"),
                ])

        def test_raises_value_error_when_middle_row_longer(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-08-14", "05:00 - 06:00", "33.1"),
                    raw_row("2024-08-14", "06:00 - 08:00", "44.65"),
                    raw_row("2024-08-14", "08:00 - 09:00", "55.2"),
                ])

        def test_raises_value_error_when_last_row_longer(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-08-14", "10:00 - 11:00", "66.75"),
                    raw_row("2024-08-14", "11:00 - 12:00", "64.3"),
                    raw_row("2024-08-14", "12:00 - 14:00", "59.9"),
                ])

        def test_raises_value_error_when_only_two_rows(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-08-14", "15:00 - 16:00", "57.45"),
                    raw_row("2024-08-14", "16:00 - 18:00", "71.8"),
                ])

    class TestInvalidInput:
        def test_raises_value_error_when_no_rows(self):
            with pytest.raises(ValueError):
                clean_dayahead_prices([])

        @pytest.mark.parametrize("missing_key", ["Date", "Delivery Period", "Price"])
        def test_raises_key_error_when_required_key_missing(self, missing_key: str):
            row = raw_row("2024-04-22", "08:00 - 09:00", "23.45")
            del row[missing_key]
            with pytest.raises(KeyError):
                clean_dayahead_prices([row])

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
                clean_dayahead_prices([
                    raw_row(row_date, "05:00 - 06:00", "31.2"),
                    raw_row(row_date, "06:00 - 07:00", "33.8"),
                    raw_row(row_date, "07:00 - 08:00", "36.1"),
                ])

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
                clean_dayahead_prices([
                    raw_row("2024-05-27", "12:00 - 13:00", "48.9"),
                    raw_row("2024-05-27", delivery_period, "51.3"),
                    raw_row("2024-05-27", "14:00 - 15:00", "49.7"),
                ])

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
                clean_dayahead_prices([
                    raw_row("2024-07-03", "17:00 - 18:00", price),
                    raw_row("2024-07-03", "18:00 - 19:00", "88.25"),
                    raw_row("2024-07-03", "19:00 - 20:00", "92.4"),
                ])

        @pytest.mark.parametrize(
            "price",
            [
                pytest.param("inf", id="inf"),
                pytest.param("-inf", id="negative_inf"),
                pytest.param("nan", id="nan"),
            ],
        )
        def test_raises_value_error_when_price_not_finite(self, price: str):
            with pytest.raises(ValueError):
                clean_dayahead_prices([
                    raw_row("2024-09-30", "20:00 - 21:00", "61.15"),
                    raw_row("2024-09-30", "21:00 - 22:00", "57.6"),
                    raw_row("2024-09-30", "22:00 - 23:00", price),
                ])


class TestDayaheadSql:
    class TestValidInput:
        def test_returns_query_for_resource_and_date_range(self):
            assert dayahead_sql("49257836-7412-4474-9c0e-c121a092d0b1", d(2026, 3, 4), d(2026, 3, 19)) == (
                'SELECT "Date", "Delivery Period", "Price" FROM "49257836-7412-4474-9c0e-c121a092d0b1" '
                "WHERE \"Date\" >= '2026-03-04' AND \"Date\" <= '2026-03-19'"
            )
