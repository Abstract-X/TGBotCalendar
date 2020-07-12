from typing import Optional, Dict
import calendar

from tgbotcalendar import exceptions


RUS_MONDAY = "Пн"
RUS_TUESDAY = "Вт"
RUS_WEDNESDAY = "Ср"
RUS_THURSDAY = "Чт"
RUS_FRIDAY = "Пт"
RUS_SATURDAY = "Сб"
RUS_SUNDAY = "Вс"

ENG_MONDAY = "Mon"
ENG_TUESDAY = "Tue"
ENG_WEDNESDAY = "Wed"
ENG_THURSDAY = "Thu"
ENG_FRIDAY = "Fri"
ENG_SATURDAY = "Sat"
ENG_SUNDAY = "Sun"

RUS_DAYS_OF_WEEK = (RUS_MONDAY, RUS_TUESDAY, RUS_WEDNESDAY,
                    RUS_THURSDAY, RUS_FRIDAY, RUS_SATURDAY, RUS_SUNDAY)
ENG_DAYS_OF_WEEK_STARTING_ON_SUNDAY = (ENG_SUNDAY, ENG_MONDAY, ENG_TUESDAY,
                                       ENG_WEDNESDAY, ENG_THURSDAY, ENG_FRIDAY, ENG_SATURDAY)
ENG_DAYS_OF_WEEK_STARTING_ON_MONDAY = (ENG_MONDAY, ENG_TUESDAY, ENG_WEDNESDAY,
                                       ENG_THURSDAY, ENG_FRIDAY, ENG_SATURDAY, ENG_SUNDAY)

RUS_MONTHS_MAPPING = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь"
}
ENG_MONTHS_MAPPING = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}


class BaseFormatter:

    def __init__(self, *, header_template: str = "{current_month} {current_year}",
                 previous_month_text: str = "«",
                 next_month_text: str = "»",
                 reset_text: str = "Clear",
                 confirm_text: str = "Confirm",
                 months_mapping: Optional[Dict[int, str]] = None,
                 months_is_uppercase: bool = False,
                 include_days_of_week: bool = True,
                 first_day_of_week: int = calendar.MONDAY,
                 days_of_week: tuple = ENG_DAYS_OF_WEEK_STARTING_ON_MONDAY,
                 days_of_week_is_uppercase: bool = False):

        self._check_fields_is_not_empty(header_template, previous_month_text,
                                        next_month_text, reset_text, confirm_text,
                                        *days_of_week)
        if months_mapping is not None:
            self._check_fields_is_not_empty(*months_mapping.values())

        if any(i not in header_template for i in ("{current_month}", "{current_year}")):
            raise exceptions.FormatterSettingError("date placeholders not found in header template!")

        if len(days_of_week) != 7:
            raise exceptions.FormatterSettingError("quantity of days in a week should be equal to seven!")

        if months_mapping is None:
            months_mapping = ENG_MONTHS_MAPPING
        else:
            if tuple(months_mapping.keys()) != tuple(range(1, 12 + 1)):
                raise exceptions.FormatterSettingError("incorrect months numbering in 'months_mapping'!")
            elif len(set(months_mapping.values())) != 12:
                raise exceptions.FormatterSettingError("there are duplicate months in 'months_mapping'!")

        if days_of_week == ENG_DAYS_OF_WEEK_STARTING_ON_MONDAY:
            if first_day_of_week != calendar.MONDAY:
                raise exceptions.FormatterSettingError("the first day of the week starting on Monday is not Monday!")
        elif days_of_week == ENG_DAYS_OF_WEEK_STARTING_ON_SUNDAY:
            if first_day_of_week != calendar.SUNDAY:
                raise exceptions.FormatterSettingError("the first day of the week starting on Sunday is not Sunday!")

        self.header_template = header_template
        self.previous_month_text = previous_month_text
        self.next_month_text = next_month_text
        self.reset_text = reset_text
        self.confirm_text = confirm_text
        self.months_mapping = months_mapping if not months_is_uppercase else {k: v.upper()
                                                                              for k, v in months_mapping.items()}
        self.include_days_of_week = include_days_of_week
        self.first_day_of_week = first_day_of_week
        self.days_of_week = days_of_week if not days_of_week_is_uppercase else tuple((i.upper() for i in days_of_week))

    @staticmethod
    def _check_fields_is_not_empty(*fields):

        if any(not i for i in fields):
            raise exceptions.FormatterSettingError("fields for text cannot be empty!")
