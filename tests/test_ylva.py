from datetime import date

import pytest

from ylva import __version__, week_number


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.parametrize(
    "dt,exp",
    [
        (date(2022, 8, 15), 2),
        (date(2022, 8, 30), 4),
        (date(2022, 8, 31), 4),
        (date(2022, 9, 1), 0),
        (date(2022, 9, 5), 0),
        (date(2022, 9, 7), 0),
        (date(2022, 9, 8), 1),
        (date(2022, 9, 9), 1),
    ],
)
def test_week_number(dt: date, exp: int) -> None:
    assert week_number(dt) == exp
