from abc import ABC, abstractmethod
import datetime as datetimelib
from typing import Optional, List, Union, Callable, Tuple, Any
import functools
import calendar
import uuid

from tgbotcalendar.utils.callback_data.filters_parts_holder import CallbackFiltersPartsHolder
from tgbotcalendar.utils import helpers


class BaseCalendar(ABC):

    _DAYS_IN_WEEK_QUANTITY = 7

    def __init__(self, *, markup_class: Callable, button_class: Callable, formatter,
                 callback_data_build_func: Callable[[Union[str, int], Union[str, int, list, None]], str],
                 callback_filters_parts_holder: CallbackFiltersPartsHolder):

        try:
            getattr(markup_class, "row")
        except AttributeError:
            raise ValueError(f"'{repr(markup_class)}' has no attribute 'row'!")

        self._markup_class = markup_class
        self._button_class = button_class
        self._formatter = formatter
        self._calendar = calendar.Calendar(firstweekday=self._formatter.first_day_of_week)
        self._callback_data_build_func = callback_data_build_func
        self._callback_filters_parts_holder = callback_filters_parts_holder

    @abstractmethod
    def render_markup(self, *args, **kwargs):

        pass

    @abstractmethod
    def _set_available_month_cells(self, current_year: int, current_month: int,
                                   month_cells: List[Optional[datetimelib.date]],
                                   selected_dates: List[datetimelib.date]):

        pass

    @abstractmethod
    def _make_confirm_button(self, selected_dates: List[datetimelib.date]):

        pass

    @abstractmethod
    def _make_navigation_buttons(self, current_year: int, current_month: int,
                                 selected_dates: List[datetimelib.date],
                                 edge_start_date: Optional[datetimelib.date] = None,
                                 edge_end_date: Optional[datetimelib.date] = None) -> Tuple[Any, Any]:

        pass

    @abstractmethod
    def _make_month_buttons(self, current_year: int, current_month: int,
                            month_cells: List[Optional[datetimelib.date]],
                            selected_dates: List[datetimelib.date]):

        pass

    def _make_reset_button(self, selected_dates: List[datetimelib.date]):

        if selected_dates:
            button = self._make_button(self._formatter.reset_text,
                                       self._callback_filters_parts_holder.reset)
        else:
            button = self._make_pass_button()

        return button

    def _render_markup(self, current_year: int, current_month: int, *,
                       selected_dates: List[datetimelib.date],
                       edge_start_date: Optional[datetimelib.date] = None,
                       edge_end_date: Optional[datetimelib.date] = None):

        header_button = self._make_header_button(current_year, current_month)
        days_of_week_buttons = self._make_days_of_week_buttons() if self._formatter.include_days_of_week else None
        month_cells = self._get_month_cells(current_year, current_month)
        self._cut_edges_of_month_cells(current_year, current_month,
                                       month_cells=month_cells,
                                       edge_start_date=edge_start_date,
                                       edge_end_date=edge_end_date)
        self._set_available_month_cells(current_year, current_month, month_cells, selected_dates)
        month_buttons = self._make_month_buttons(current_year, current_month, month_cells, selected_dates)
        previous_month_button, next_month_button = self._make_navigation_buttons(current_year, current_month,
                                                                                 selected_dates=selected_dates,
                                                                                 edge_start_date=edge_start_date,
                                                                                 edge_end_date=edge_end_date)
        reset_button = self._make_reset_button(selected_dates)
        confirm_button = self._make_confirm_button(selected_dates)

        markup = self._build_markup(
            header_button=header_button,
            month_buttons=month_buttons,
            previous_month_button=previous_month_button,
            next_month_button=next_month_button,
            reset_button=reset_button,
            confirm_button=confirm_button,
            days_of_week_buttons=days_of_week_buttons
        )

        return markup

    def _get_empty_markup(self):

        return self._markup_class(row_width=self._DAYS_IN_WEEK_QUANTITY)

    def _build_markup(self, *, header_button, month_buttons, previous_month_button,
                      next_month_button, reset_button, confirm_button, days_of_week_buttons=None):

        markup = self._get_empty_markup()

        markup.row(header_button)
        if days_of_week_buttons is not None:
            markup.row(*days_of_week_buttons)
        for dates_row_buttons in helpers.slice_list(month_buttons, self._DAYS_IN_WEEK_QUANTITY):
            markup.row(*dates_row_buttons)
        markup.row(previous_month_button, next_month_button)
        markup.row(reset_button, confirm_button)

        return markup

    def _make_button(self, text: str, filter_part: Union[str, int],
                     data: Union[str, list, None] = None):

        return self._button_class(
            text=text,
            callback_data=self._callback_data_build_func(filter_part, data)
        )

    def _make_pass_button(self, text: str = " "):

        return self._make_button(text, self._callback_filters_parts_holder.pass_, str(uuid.uuid4()))

    def _make_header_button(self, year: int, month: int):

        return self._make_pass_button(self._formatter.header_template.format(
            current_month=self._formatter.months_mapping[month],
            current_year=year)
        )

    @functools.lru_cache(maxsize=1)
    def _make_days_of_week_buttons(self):

        return [self._make_pass_button(i) for i in self._formatter.days_of_week]

    def _get_month_cells(self, year: int, month: int) -> List[Optional[datetimelib.date]]:

        matrix = self._calendar.monthdayscalendar(year, month)
        cells = []

        for row in matrix:
            cells.extend(row)

        for index, cell in enumerate(cells):
            cells.pop(index)
            if cell == 0:
                cells.insert(index, None)
            else:
                cells.insert(index, datetimelib.date(year, month, cell))

        return cells

    @staticmethod
    def _cut_edges_of_month_cells(current_year: int, current_month: int,
                                  month_cells: List[Optional[datetimelib.date]],
                                  edge_start_date: Optional[datetimelib.date] = None,
                                  edge_end_date: Optional[datetimelib.date] = None):

        pop_ranges = []

        if edge_start_date is not None:
            if (current_year, current_month) == (edge_start_date.year, edge_start_date.month):
                start_split_index = month_cells.index(edge_start_date)
                pop_ranges.append(range(start_split_index))
        if edge_end_date is not None:
            if (current_year, current_month) == (edge_end_date.year, edge_end_date.month):
                end_split_index = month_cells.index(edge_end_date)
                pop_ranges.append(range(end_split_index + 1, len(month_cells)))

        for range_ in pop_ranges:
            for i in range_:
                month_cells.pop(i)
                month_cells.insert(i, None)

    def _make_previous_month_button(self, current_year: int, current_month: int):

        return self._make_button(self._formatter.previous_month_text,
                                 self._callback_filters_parts_holder.previous_month,
                                 list(helpers.make_offset_previous_month(current_year, current_month)))

    def _make_next_month_button(self, current_year: int, current_month: int):

        return self._make_button(self._formatter.next_month_text,
                                 self._callback_filters_parts_holder.next_month,
                                 list(helpers.make_offset_next_month(current_year, current_month)))
