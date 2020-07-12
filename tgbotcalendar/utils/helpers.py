import datetime as datetimelib
from typing import List, Tuple, Union


def serialize_date(date: datetimelib.date) -> str:

    return date.strftime(r"%d.%m.%Y")


def deserialize_date(date: str) -> datetimelib.date:

    day, month, year = map(int, date.split("."))
    return datetimelib.date(year, month, day)


def make_offset_previous_month(year: int, month: int) -> Tuple[int, int]:

    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1

    return year, month


def make_offset_next_month(year: int, month: int) -> Tuple[int, int]:

    if month == 12:
        year += 1
        month = 1
    else:
        month += 1

    return year, month


def slice_list(list_: list, part_quantity: int) -> list:

    parts = []

    if part_quantity > 0:
        start_step = 0
        end_step = part_quantity
        while start_step < len(list_):
            part = list_[start_step:end_step]
            parts.append(part)
            start_step += part_quantity
            end_step += part_quantity

    return parts


def get_period_dates(start_date: Union[datetimelib.date, str],
                     end_date: Union[datetimelib.date, str]) -> List[datetimelib.date]:

    if isinstance(start_date, str):
        start_date = deserialize_date(start_date)
    if isinstance(end_date, str):
        end_date = deserialize_date(end_date)

    period_dates = []
    period_date = start_date
    while period_date <= end_date:
        period_dates.append(period_date)
        period_date += datetimelib.timedelta(days=1)

    return period_dates
