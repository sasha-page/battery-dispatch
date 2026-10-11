import datetime
import pytest
from data_streaming import month_ranges

d = datetime.date

class TestMonthRanges:
    class TestRangeWithinSingleMonth:
        def test_returns_single_entry_when_range_is_whole_month(self):
            assert month_ranges(d(2024, 4, 1), d(2024, 4, 30)) == {
                "2024-04": (d(2024, 4, 1), d(2024, 4, 30)),
            }

        def test_returns_single_entry_when_start_on_first_day_and_end_mid_month(self):
            assert month_ranges(d(2024, 3, 1), d(2024, 3, 20)) == {
                "2024-03": (d(2024, 3, 1), d(2024, 3, 20)),
            }

        def test_returns_single_entry_when_start_mid_month_and_end_on_last_day(self):
            assert month_ranges(d(2024, 3, 5), d(2024, 3, 31)) == {
                "2024-03": (d(2024, 3, 5), d(2024, 3, 31)),
            }

        def test_returns_single_entry_when_both_dates_mid_month(self):
            assert month_ranges(d(2024, 2, 5), d(2024, 2, 20)) == {
                "2024-02": (d(2024, 2, 5), d(2024, 2, 20)),
            }

        def test_returns_single_day_entry_when_start_equals_end(self):
            assert month_ranges(d(2024, 5, 17), d(2024, 5, 17)) == {
                "2024-05": (d(2024, 5, 17), d(2024, 5, 17)),
            }

    class TestRangeAcrossMonths:
        def test_returns_unclipped_entries_when_start_on_first_day_and_end_on_last_day(self):
            assert month_ranges(d(2024, 3, 1), d(2024, 5, 31)) == {
                "2024-03": (d(2024, 3, 1), d(2024, 3, 31)),
                "2024-04": (d(2024, 4, 1), d(2024, 4, 30)),
                "2024-05": (d(2024, 5, 1), d(2024, 5, 31)),
            }

        def test_clips_final_entry_when_start_on_first_day_and_end_mid_month(self):
            assert month_ranges(d(2024, 3, 1), d(2024, 5, 15)) == {
                "2024-03": (d(2024, 3, 1), d(2024, 3, 31)),
                "2024-04": (d(2024, 4, 1), d(2024, 4, 30)),
                "2024-05": (d(2024, 5, 1), d(2024, 5, 15)),
            }

        def test_clips_first_entry_when_start_mid_month_and_end_on_last_day(self):
            assert month_ranges(d(2024, 3, 10), d(2024, 5, 31)) == {
                "2024-03": (d(2024, 3, 10), d(2024, 3, 31)),
                "2024-04": (d(2024, 4, 1), d(2024, 4, 30)),
                "2024-05": (d(2024, 5, 1), d(2024, 5, 31)),
            }

        def test_clips_first_and_final_entries_when_both_dates_mid_month(self):
            assert month_ranges(d(2024, 3, 10), d(2024, 5, 15)) == {
                "2024-03": (d(2024, 3, 10), d(2024, 3, 31)),
                "2024-04": (d(2024, 4, 1), d(2024, 4, 30)),
                "2024-05": (d(2024, 5, 1), d(2024, 5, 15)),
            }

    class TestStartOnLastDayOfMonthAndEndOnFirstDayOfMonth:
        def test_returns_single_day_entries_for_adjacent_months(self):
            assert month_ranges(d(2024, 3, 31), d(2024, 4, 1)) == {
                "2024-03": (d(2024, 3, 31), d(2024, 3, 31)),
                "2024-04": (d(2024, 4, 1), d(2024, 4, 1)),
            }

        def test_returns_full_months_between_single_day_entries(self):
            assert month_ranges(d(2024, 1, 31), d(2024, 3, 1)) == {
                "2024-01": (d(2024, 1, 31), d(2024, 1, 31)),
                "2024-02": (d(2024, 2, 1), d(2024, 2, 29)),
                "2024-03": (d(2024, 3, 1), d(2024, 3, 1)),
            }

    class TestRangeAcrossYears:
        def test_returns_one_entry_per_month_across_two_years(self):
            assert month_ranges(d(2023, 11, 15), d(2024, 2, 10)) == {
                "2023-11": (d(2023, 11, 15), d(2023, 11, 30)),
                "2023-12": (d(2023, 12, 1), d(2023, 12, 31)),
                "2024-01": (d(2024, 1, 1), d(2024, 1, 31)),
                "2024-02": (d(2024, 2, 1), d(2024, 2, 10)),
            }

        def test_returns_one_unique_entry_per_month_across_many_years(self):
            result = month_ranges(d(2021, 6, 20), d(2024, 3, 5))
            assert len(result) == 34

        def test_returns_single_day_entries_for_adjacent_days_at_year_boundary(self):
            assert month_ranges(d(2023, 12, 31), d(2024, 1, 1)) == {
                "2023-12": (d(2023, 12, 31), d(2023, 12, 31)),
                "2024-01": (d(2024, 1, 1), d(2024, 1, 1)),
            }

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
            assert month_ranges(d(year, 2, 1), d(year, 2, last_day)) == {
                f"{year}-02": (d(year, 2, 1), d(year, 2, last_day)),
            }

        def test_includes_leap_day_in_leap_year_when_range_extends_into_march(self):
            assert month_ranges(d(2024, 2, 1), d(2024, 3, 31)) == {
                "2024-02": (d(2024, 2, 1), d(2024, 2, 29)),
                "2024-03": (d(2024, 3, 1), d(2024, 3, 31)),
            }

        def test_excludes_leap_day_in_common_year_between_clipped_months(self):
            assert month_ranges(d(2023, 1, 31), d(2023, 3, 1)) == {
                "2023-01": (d(2023, 1, 31), d(2023, 1, 31)),
                "2023-02": (d(2023, 2, 1), d(2023, 2, 28)),
                "2023-03": (d(2023, 3, 1), d(2023, 3, 1)),
            }

        def test_returns_correct_lengths_for_every_month_in_a_year(self):
            result = month_ranges(d(2023, 1, 1), d(2023, 12, 31))
            assert [last.day for _, last in result.values()] == [
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
