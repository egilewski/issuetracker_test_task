"""Utils for `core` app."""
from datetime import timedelta


def round_timedelta_to_minute(
        timedelta_: (timedelta, "Value to round")) -> timedelta:
    """Return provided timedelta rounded to the nearest minute."""
    return timedelta(minutes=round(timedelta_ / timedelta(minutes=1)))
