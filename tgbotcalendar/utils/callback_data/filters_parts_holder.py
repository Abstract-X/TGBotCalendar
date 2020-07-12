from typing import Union


class CallbackFiltersPartsHolder:

    def __init__(self, *, pass_: Union[str, int], previous_month: Union[str, int],
                 next_month: Union[str, int], select_date: Union[str, int],
                 reset: Union[str, int], confirm: Union[str, int]):

        self.pass_ = pass_
        self.previous_month = previous_month
        self.next_month = next_month
        self.select_date = select_date
        self.reset = reset
        self.confirm = confirm
