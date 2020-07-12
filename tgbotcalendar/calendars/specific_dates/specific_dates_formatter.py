import calendar
from typing import Optional, Dict

from tgbotcalendar.calendars.base.base_formatter import BaseFormatter, ENG_DAYS_OF_WEEK_STARTING_ON_MONDAY


class SpecificDatesFormatter(BaseFormatter):

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
                 days_of_week_is_uppercase: bool = False,
                 selected_date_text: str = "✅"):

        super().__init__(header_template=header_template, previous_month_text=previous_month_text,
                         next_month_text=next_month_text, reset_text=reset_text, confirm_text=confirm_text,
                         months_mapping=months_mapping, months_is_uppercase=months_is_uppercase,
                         include_days_of_week=include_days_of_week, first_day_of_week=first_day_of_week,
                         days_of_week=days_of_week, days_of_week_is_uppercase=days_of_week_is_uppercase)
        self._check_fields_is_not_empty(selected_date_text)
        self.selected_date_text = selected_date_text
