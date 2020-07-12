from typing import Callable
import datetime
import enum

from tgbotcalendar import (PeriodDatesCalendar, PeriodDatesFormatter, CallbackFiltersPartsHolder,
                           make_offset_previous_month, make_offset_next_month, get_period_dates,
                           serialize_date, deserialize_date)
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram_callback_factory import make_callback_data, CallbackDataFilter, CallbackFactoryMiddleware


BOT_TOKEN = "..."  # insert your token here


class CallbackFilterKey(enum.IntEnum):
    """ Keys for filtering callback_data. """

    PASS = 1
    PREVIOUS_MONTH = 2
    NEXT_MONTH = 3
    SELECT_DATE = 4
    RESET = 5
    CONFIRM = 6


bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
dispatcher.filters_factory.bind(CallbackDataFilter, event_handlers=[dispatcher.callback_query_handlers])
dispatcher.middleware.setup(CallbackFactoryMiddleware())

# creating a calendar factory
calendar = PeriodDatesCalendar(
    markup_class=InlineKeyboardMarkup,
    button_class=InlineKeyboardButton,
    formatter=PeriodDatesFormatter(),
    callback_data_build_func=make_callback_data,
    callback_filters_parts_holder=CallbackFiltersPartsHolder(
        pass_=CallbackFilterKey.PASS.value,
        previous_month=CallbackFilterKey.PREVIOUS_MONTH.value,
        next_month=CallbackFilterKey.NEXT_MONTH.value,
        select_date=CallbackFilterKey.SELECT_DATE.value,
        reset=CallbackFilterKey.RESET.value,
        confirm=CallbackFilterKey.CONFIRM.value
    )
)


def render_calendar_markup(data: dict):

    today = datetime.date.today()  # dates for selection will start from today
    return calendar.render_markup(data["current_year"], data["current_month"],
                                  selected_start_date=data["selected_start_date"],
                                  selected_end_date=data["selected_end_date"],
                                  edge_start_date=today)


@dispatcher.message_handler(commands=["start"])
async def handle_start_command(event: Message, state: FSMContext):

    today = datetime.datetime.today()

    # setting initial values for calendar
    data = {
        "selected_start_date": None,
        "selected_end_date": None,
        "current_year": today.year,
        "current_month": today.month
    }
    await state.update_data(data)

    calendar_message_id = data.get("calendar_message_id")
    if calendar_message_id is not None:
        await bot.delete_message(event.from_user.id, calendar_message_id)

    message = await bot.send_message(event.from_user.id, "🏁 Please select a start date for the period:",
                                     reply_markup=render_calendar_markup(data))
    await state.update_data({
        "calendar_message_id": message.message_id
    })


@dispatcher.callback_query_handler(callback_data=CallbackFilterKey.PASS)
async def handle_pass(event: CallbackQuery):

    await bot.answer_callback_query(event.id)


async def handle_offset_month(event: CallbackQuery, state: FSMContext, make_offset_func: Callable):

    data = await state.get_data()
    data["current_year"], data["current_month"] = make_offset_func(data["current_year"],
                                                                   data["current_month"])
    await state.update_data(data)
    await bot.answer_callback_query(event.id)
    await bot.edit_message_reply_markup(event.from_user.id, event.message.message_id,
                                        reply_markup=render_calendar_markup(data))


@dispatcher.callback_query_handler(callback_data=CallbackFilterKey.PREVIOUS_MONTH)
async def handle_previous_month(event: CallbackQuery, state: FSMContext):

    await handle_offset_month(event, state, make_offset_previous_month)


@dispatcher.callback_query_handler(callback_data=CallbackFilterKey.NEXT_MONTH)
async def handle_next_month(event: CallbackQuery, state: FSMContext):

    await handle_offset_month(event, state, make_offset_next_month)


@dispatcher.callback_query_handler(callback_data=CallbackFilterKey.SELECT_DATE)
async def handle_select_date(event: CallbackQuery, state: FSMContext):

    selected_date = event.data
    data = await state.get_data()

    if data["selected_start_date"] is None:
        data["selected_start_date"] = selected_date
        text = "🏁 Fine! Now select the end date:"
    else:
        data["selected_end_date"] = selected_date
        text = "✅ Ok, period received! Confirm your selection, or start over."

    await state.update_data(data)
    await bot.answer_callback_query(event.id)
    await bot.edit_message_text(text, event.from_user.id, event.message.message_id,
                                reply_markup=render_calendar_markup(data))


@dispatcher.callback_query_handler(callback_data=CallbackFilterKey.RESET)
async def handle_reset(event: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    data["selected_start_date"] = None
    data["selected_end_date"] = None
    await state.update_data(data)
    await bot.answer_callback_query(event.id)
    await bot.edit_message_text("🏁 Please select a start date for the period:",
                                event.from_user.id, event.message.message_id,
                                reply_markup=render_calendar_markup(data))


@dispatcher.callback_query_handler(callback_data=CallbackFilterKey.CONFIRM)
async def handle_confirm(event: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    data["calendar_message_id"] = None
    await state.update_data(data)

    dates_text = "\n".join([serialize_date(i) for i in get_period_dates(data["selected_start_date"],
                                                                        data["selected_end_date"])])
    await bot.answer_callback_query(event.id)
    await bot.edit_message_text(f"✅ You have selected dates:\n\n{dates_text}", event.from_user.id,
                                event.message.message_id)


if __name__ == '__main__':
    print("Started!")
    executor.start_polling(dispatcher, fast=False)
