import datetime as datetimelib
from typing import Optional, List, Callable, Union, Tuple, Any

from tgbotcalendar.calendars.base.base_calendar import BaseCalendar
from tgbotcalendar.calendars.specific_dates.specific_dates_formatter import SpecificDatesFormatter
from tgbotcalendar.utils.callback_data.filters_parts_holder import CallbackFiltersPartsHolder
from tgbotcalendar.utils import helpers


class SpecificDatesCalendar(BaseCalendar):

    def __init__(self, *, markup_class: Callable, button_class: Callable, formatter: SpecificDatesFormatter,
                 callback_data_build_func: Callable[[Union[str, int], Union[str, int, list, None]], str],
                 callback_filters_parts_holder: CallbackFiltersPartsHolder):

        super().__init__(markup_class=markup_class, button_class=button_class,
                         formatter=formatter, callback_data_build_func=callback_data_build_func,
                         callback_filters_parts_holder=callback_filters_parts_holder)

    def render_markup(self, current_year: int, current_month: int, *,
                      selected_dates: List[Union[datetimelib.date, str]],
                      edge_start_date: Optional[datetimelib.date] = None,
                      edge_end_date: Optional[datetimelib.date] = None):

        deserialized_selected_dates = []
        for date in selected_dates:
            if isinstance(date, str):
                deserialized_date = helpers.deserialize_date(date)
            else:
                deserialized_date = date
            deserialized_selected_dates.append(deserialized_date)

        return self._render_markup(current_year, current_month,
                                   selected_dates=deserialized_selected_dates,
                                   edge_start_date=edge_start_date,
                                   edge_end_date=edge_end_date)

    def _set_available_month_cells(self, current_year: int, current_month: int,
                                   month_cells: List[Optional[datetimelib.date]],
                                   selected_dates: List[datetimelib.date]):

        pass

    def _make_confirm_button(self, selected_dates: List[datetimelib.date]):

        if selected_dates:
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
        if edge_end_date is not None:
            if current_year_month == (edge_end_date.year, edge_end_date.month):
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
                    button_text = self._formatter.selected_date_text
                else:
                    button_text = str(cell.day)
                button = self._make_button(button_text, self._callback_filters_parts_holder.select_date,
                                           helpers.serialize_date(cell))
            else:
                button = self._make_pass_button()
            buttons.append(button)

        return buttons
