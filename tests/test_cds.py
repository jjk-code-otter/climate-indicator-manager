import pytest
from climind.fetchers.fetcher_cds import pick_months
from datetime import datetime

class TestPickMonths:

    def test_earlier_year(self):

        now = datetime(2022, 6, 8)
        months = pick_months(2002, now)
        assert len(months) == 12
        for m in range(12):
            assert months[m] == f'{m+1:02d}'

    def test_this_year_after_seventh(self):

        now = datetime(2022, 6, 8)
        months = pick_months(2022, now)
        assert len(months) == 5
        for m in range(5):
            assert months[m] == f'{m+1:02d}'

    def test_this_year_before_seventh(self):

        now = datetime(2022, 6, 3)
        months = pick_months(2022, now)
        assert len(months) == 4
        for m in range(4):
            assert months[m] == f'{m+1:02d}'

    def test_january_empty_list(self):

        now = datetime(2022, 1, 2)
        months = pick_months(2022, now)
        assert len(months) == 0

    def test_january_empty_list_after_seventh(self):

        now = datetime(2022, 1, 8)
        months = pick_months(2022, now)
        assert len(months) == 0
