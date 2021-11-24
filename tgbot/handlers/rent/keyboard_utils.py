from telegram import ReplyKeyboardMarkup, KeyboardButton

from .static_text import (
    addresses,
    categories,
    dimensions,
    stuff_categories,
    period_12_months,
    reserve,
    more_or_less_month,
    period_3_weeks,
    period_6_months,
    skip_change_pd,
    request_contact_button,
    send_invoice,
    consent_button,
    yes_no
)


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def make_yes_no_keyboard() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(answer) for answer in yes_no]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_addresses() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(address) for address in addresses]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_category() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(category) for category in categories]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_confirmation() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(reser) for reser in reserve]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


# Branch 'Другое'
def make_keyboard_with_dimensions() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(dimension) for dimension in dimensions]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_period() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(address) for address in period_12_months]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


# Branch 'Сезонные вещи'
def make_keyboard_with_stuff_categories() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(category) for category in stuff_categories]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_stuff_period_1(is_wheels) -> ReplyKeyboardMarkup:
    if is_wheels:
        buttons = [KeyboardButton(choose) for choose in more_or_less_month[1:]]
    else:
        buttons = [KeyboardButton(choose) for choose in more_or_less_month]
    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_stuff_period_2_weeks() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(week) for week in period_3_weeks]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=1),
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return reply_markup


def make_keyboard_with_stuff_period_2_months() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(month) for month in period_6_months]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_keyboard_with_skip_change_pd() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(month) for month in skip_change_pd]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


# Личные данные
def make_keyboard_with_consent() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(button) for button in consent_button]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return reply_markup


def make_keyboard_to_get_contact() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(button, request_contact=True) for button in
               request_contact_button]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=1),
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return reply_markup


# Оплата
def make_keyboard_with_invoice() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(button) for button in send_invoice]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return reply_markup
