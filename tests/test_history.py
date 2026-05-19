from datetime import date
import unittest

from github_trend_lab.history import iter_days


class HistoryTests(unittest.TestCase):
    def test_iter_days_is_inclusive(self):
        days = list(iter_days(date(2026, 1, 1), date(2026, 1, 3)))

        self.assertEqual(days, [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)])


if __name__ == "__main__":
    unittest.main()
