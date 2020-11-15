import calendar
import datetime as datetimelib
from typing import Optional, List, Callable, Union, Tuple, Any

from tgbotcalendar.calendars.base.base_calendar import BaseCalendar
from tgbotcalendar.calendars.period_dates.period_dates_formatter import PeriodDatesFormatter
from tgbotcalendar.utils.callback_data.filters_parts_holder import CallbackFiltersPartsHolder
from tgbotcalendar.utils import helpers


class PeriodDatesCalendar(BaseCalendar):

    def __init__(self, *, markup_class: Callable, button_class: Callable, formatter: PeriodDatesFormatter,
                 callback_data_build_func: Callable[[Union[str, int], Union[str, int, list, None]], str],
                 callback_filters_parts_holder: CallbackFiltersPartsHolder):

        super().__init__(markup_class=markup_class, button_class=button_class,
                         formatter=formatter, callback_data_build_func=callback_data_build_func,
                         callback_filters_parts_holder=callback_filters_parts_holder)

    def render_markup(self, current_year: int, current_month: int, *,
                      selected_start_date: Union[datetimelib.date, str, None] = None,
                      selected_end_date: Union[datetimelib.date, str, None] = None,
                      edge_start_date: Optional[datetimelib.date] = None,
                      edge_end_date: Optional[datetimelib.date] = None):

        if isinstance(selected_start_date, str):
            selected_start_date = helpers.deserialize_date(selected_start_date)
        if isinstance(selected_end_date, str):
            selected_end_date = helpers.deserialize_date(selected_end_date)

        selected_dates = []
        if selected_start_date is not None:
            if selected_end_date is None:
                selected_dates.append(selected_start_date)
            else:
                if selected_start_date > selected_end_date:
                    raise ValueError("selected start date can't be later than selected end date!")
                period_dates = helpers.get_period_dates(selected_start_date, selected_end_date)
                selected_dates.extend(period_dates)

        return self._render_markup(current_year, current_month,
                                   selected_dates=selected_dates,
                                   edge_start_date=edge_start_date,
                                   edge_end_date=edge_end_date)

    def _set_available_month_cells(self, current_year: int, current_month: int,
                                   month_cells: List[Optional[datetimelib.date]],
                                   selected_dates: List[datetimelib.date]):

        excess_cells = []
        month_dates = [i for i in month_cells if i is not None]
        current_year_month = (current_year, current_month)

        if selected_dates:
            start_date = selected_dates[0]
            if current_year_month == (start_date.year, start_date.month):
                start_index = month_dates.index(start_date)
                excess_cells.extend(month_dates[:start_index])
        if len(selected_dates) > 1:
            end_date = selected_dates[-1]
            if current_year_month == (end_date.year, end_date.month):
                end_index = month_dates.index(end_date)
                excess_cells.extend(month_dates[end_index + 1:])

        for index, cell in enumerate(month_cells):
            if (cell is not None) and (cell in excess_cells):
                month_cells[index] = None

    def _make_confirm_button(self, selected_dates: List[datetimelib.date]):

        if len(selected_dates) > 1:
            button = self._make_button(f"{self._formatter.confirm_text} ({len(selected_dates)})",
                                       self._callback_filters_parts_holder.confirm)
        else:
            button = self._make_pass_button()

        return button

    def _make_navigation_buttons(self, current_year: int, current_month: int,
                                 selected_dates: List[datetimelib.date],
                                 edge_start_date: Optional[datetimelib.date] = None,
                                 edge_end_date: Optional[datetimelib.date] = None) -> Tuple[Any, Any]:

        previous_month_button = None
        next_month_button = None
        current_year_month = (current_year, current_month)

        if edge_start_date is not None:
            if current_year_month == (edge_start_date.year, edge_start_date.month):
                previous_month_button = self._make_pass_button()
        if selected_dates:
            start_date = selected_dates[0]
            if current_year_month == (start_date.year, start_date.month):
                previous_month_button = self._make_pass_button()

        if edge_end_date is not None:
            if current_year_month == (edge_end_date.year, edge_end_date.month):
                next_month_button = self._make_pass_button()
        if len(selected_dates) > 1:
            end_date = selected_dates[-1]
            if current_year_month == (end_date.year, end_date.month):
                next_month_button = self._make_pass_button()

        if previous_month_button is None:
            previous_month_button = self._make_previous_month_button(current_year, current_month)
        if next_month_button is None:
            next_month_button = self._make_next_month_button(current_year, current_month)

        return previous_month_button, next_month_button

    def _make_month_buttons(self, current_year: int, current_month: int,
                            month_cells: List[Optional[datetimelib.date]],
                            selected_dates: List[datetimelib.date]):

        buttons = []

        for cell in month_cells:
            if cell is not None:
                if cell in selected_dates:
                    if cell == selected_dates[0]:
                        button_text = self._formatter.selected_start_date
                    elif (len(selected_dates) > 1) and (cell == selected_dates[-1]):
                        button_text = self._formatter.selected_end_date
                    elif cell.day in (1, calendar.monthrange(current_year, current_month)[1]):
                        button_text = "..."
                    else:
                        button_text = self._formatter.selected_period_date
                    button = self._make_pass_button(button_text)
                else:
                    button_text = str(cell.day)
                    button = self._make_button(button_text, self._callback_filters_parts_holder.select_date,
                                               helpers.serialize_date(cell))
            else:
                button = self._make_pass_button()
            buttons.append(button)

        return buttons
