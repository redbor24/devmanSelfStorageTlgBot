from datetime import date, datetime, timedelta
import os

import phonenumbers
from dateutil.relativedelta import relativedelta
from telegram import ParseMode, ShippingOption, Update, ReplyKeyboardRemove, \
    LabeledPrice
from telegram.ext import CallbackContext, ConversationHandler

from self_storage.settings import PROVIDER_TOKEN, BASE_DIR, CONSENT_PD_FILEPATH
from tgbot.models import StorageUser, Orders, StoredThing
from tgbot.handlers.rent import static_text
from .keyboard_utils import (
    make_keyboard_with_addresses,
    make_keyboard_with_category,
    make_keyboard_with_dimensions,
    make_keyboard_with_stuff_categories,
    make_keyboard_with_confirmation,
    make_keyboard_with_period,
    make_keyboard_with_stuff_period_1,
    make_keyboard_with_stuff_period_2_weeks,
    make_keyboard_with_stuff_period_2_months,
    make_keyboard_with_skip_change_pd,
    make_keyboard_with_consent,
    make_keyboard_to_get_contact,
    make_keyboard_with_invoice,
    make_yes_no_keyboard
)

from ..common.keyboard_utils import make_keyboard_for_start_command

(ADDRESS,
 CATEGORY,
 OTHER,
 SEASONAL,
 PERIOD,
 COUNT,
 PERIOD1,
 PERIOD2,
 PD,
 SELECT_PD,
 CONSENT,
 FIO,
 PHONE,
 DUL,
 BIRTHDATE,
 PAY,
 ASK_PROMO,
 GET_PROMO,
 SUMMARY) = range(19)


def send_message_with_addresses(update: Update, _):
    text = static_text.choose_address
    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_with_addresses(),
    )
    return ADDRESS


def get_store_address(update: Update, rent_description):
    address = update.message.text
    if address not in static_text.addresses:
        text = static_text.choose_address
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_addresses(),
        )
        return ADDRESS
    rent_description.bot_data['address'] = address
    rent_description.bot_data['user_telegram_id'] = update.message.from_user.id

    text = static_text.choose_category
    update.message.reply_text(
        text,
        reply_markup=make_keyboard_with_category()
    )
    return CATEGORY


def get_category(update: Update, rent_description):
    category = update.message.text
    if category not in static_text.categories:
        text = static_text.choose_category
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_category()
        )
        return CATEGORY
    rent_description.bot_data['category'] = category
    if category == static_text.categories[1]:
        text = static_text.choose_dimensions
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_dimensions()
        )
        return OTHER
    elif category == static_text.categories[0]:
        text = static_text.choose_stuff_category
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_stuff_categories()
        )
        return SEASONAL


'''Ветка другое'''


def get_dimension(update: Update, rent_description):
    dimensions = update.message.text
    if dimensions not in static_text.dimensions:
        text = static_text.choose_dimensions
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_dimensions()
        )
        return OTHER
    rent_description.bot_data[
        'dimensions'
    ] = dimensions.split(' - ')[0].split()[0]

    rent_description.bot_data['stuff_category'] = 'Другое'

    text = static_text.choose_period_months_12
    update.message.reply_text(
        text,
        reply_markup=make_keyboard_with_period()
    )
    return PERIOD


def get_period(update: Update, rent_description):
    period = update.message.text
    if period not in static_text.period_12_months:
        text = static_text.choose_period_months_12
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_period()
        )
        return PERIOD
    rent_description.bot_data['period_name'] = 'месяц'
    rent_description.bot_data['period_count'] = period.split(' ')[0]

    # Спрашиваем про промокод
    text = static_text.is_promocode
    update.message.reply_text(
        text,
        reply_markup=make_yes_no_keyboard()
    )
    return ASK_PROMO


def ask_promo(update: Update, rent_description):
    answer = update.message.text
    if answer not in static_text.yes_no:
        update.message.reply_text(
            text=static_text.yes_no,
            reply_markup=make_yes_no_keyboard(),
        )
        return ASK_PROMO

    print(f'ask_promo().answer: {answer}')
    # У пользователя нет промокода - переходим к подтверждению заказа
    if static_text.yes_no.index(answer) == 1:  # Нет (промокода)
        rent_description.bot_data['promo_code'] = ''
        text = static_text.order_confirmation
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_confirmation()
        )
        return SUMMARY

    text = static_text.input_promocode
    update.message.reply_text(text)
    return GET_PROMO


def get_promo(update: Update, rent_description):
    promo = update.message.text
    if promo not in static_text.promos:
        update.message.reply_text(
            text=static_text.bad_promo + '\n' + static_text.is_promocode,
            reply_markup=make_yes_no_keyboard(),
        )
        return ASK_PROMO

    rent_description.bot_data['promo_code'] = promo

    update.message.reply_text(
        text=static_text.good_promo + '\n' + static_text.order_confirmation,
        reply_markup=make_keyboard_with_confirmation()
    )
    return SUMMARY


def show_summary(update: Update, rent_description):
    if rent_description.bot_data['category'] == 'Сезонные вещи':
        thing = rent_description.bot_data['stuff_category']
        things_count = rent_description.bot_data['stuff_count']
        unit_name = 'шт.'
    else:
        thing = rent_description.bot_data['category']
        things_count = rent_description.bot_data['dimensions']
        unit_name = 'м.кв.'

    if rent_description.bot_data.get('promo_code'):
        promo_msg_part = f'Промокод: {rent_description.bot_data["promo_code"]}'
    else:
        promo_msg_part = 'Промокод: нет'

    message = 'Ваш заказ:\n' \
        f'  Склад: {rent_description.bot_data["address"]}\n' \
        f'  Категория вещи: {rent_description.bot_data["category"]}\n' \
        f'  Вещь: {thing}, {things_count} {unit_name}\n' \
        f'  Длительность хранения: ' \
              f' {rent_description.bot_data["period_count"]}, ' \
              f' {rent_description.bot_data["period_name"]}\n' \
        f'{promo_msg_part}'
    update.message.reply_text(
        text=message,
        reply_markup=make_keyboard_with_confirmation()
    )
    return PD


'''Конец ветки другое'''

'''Ветка сезонные вещи'''


def get_stuff_category(update: Update, rent_description):
    stuff_category = update.message.text
    if stuff_category not in static_text.stuff_categories:
        text = static_text.choose_stuff_category
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_stuff_categories()
        )
        return SEASONAL
    rent_description.bot_data['stuff_category'] = stuff_category

    text = static_text.choose_stuff_count.format(
        price=static_text.price[stuff_category]
    )
    update.message.reply_text(
        text
    )
    return COUNT


def get_stuff_count(update: Update, rent_description):
    stuff_count = update.message.text
    if not stuff_count.isdigit() or stuff_count < '1':
        stuff_category = rent_description.bot_data['stuff_category']
        text = static_text.choose_stuff_count.format(
            price=static_text.price[stuff_category]
        )
        update.message.reply_text(
            text
        )
        return COUNT
    stuff_category = rent_description.bot_data['stuff_category']
    is_wheels = (stuff_category == 'Колеса')
    if is_wheels and int(stuff_count) % 4 != 0:
        text = static_text.choose_stuff_count_error_wheels
        update.message.reply_text(
            text
        )
        return COUNT

    if is_wheels:
        rent_description.bot_data['stuff_count'] = str(int(stuff_count) // 4)
    else:
        rent_description.bot_data['stuff_count'] = stuff_count

    text = static_text.choose_more_or_less_month
    update.message.reply_text(
        text,
        reply_markup=make_keyboard_with_stuff_period_1(is_wheels)
    )
    return PERIOD1


def get_period_name(update: Update, rent_description):
    period = update.message.text
    if period not in static_text.more_or_less_month:
        stuff_category = rent_description.bot_data['stuff_category']
        is_wheels = (stuff_category == 'Колеса')
        text = static_text.choose_more_or_less_month
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_stuff_period_1(is_wheels)
        )
        return PERIOD1

    if period == static_text.more_or_less_month[0]:
        period_name = 'неделя'
        keyboard = make_keyboard_with_stuff_period_2_weeks()
    else:
        period_name = 'месяц'
        keyboard = make_keyboard_with_stuff_period_2_months()
    rent_description.bot_data['period_name'] = period_name

    text = static_text.specify_period
    update.message.reply_text(
        text,
        reply_markup=keyboard
    )
    return PERIOD2


def get_period_count(update: Update, rent_description):
    period_count = update.message.text
    period_name = rent_description.bot_data['period_name']
    if (period_name == 'неделя' and
        period_count not in static_text.period_3_weeks):
        keyboard = make_keyboard_with_stuff_period_2_weeks()
        text = static_text.specify_period
        update.message.reply_text(
            text,
            reply_markup=keyboard
        )
        return PERIOD2
    elif (period_name == 'месяц' and
          period_count not in static_text.period_6_months):
        keyboard = make_keyboard_with_stuff_period_2_months()
        text = static_text.specify_period
        update.message.reply_text(
            text,
            reply_markup=keyboard
        )
        return PERIOD2

    rent_description.bot_data['period_count'] = period_count.split()[0]

    text = static_text.is_promocode
    update.message.reply_text(
        text,
        reply_markup=make_yes_no_keyboard()
    )
    return ASK_PROMO


'''Конец ветки сезонные вещи'''

''' Начало сценария после нажатия кнопки Забронировать. Ввод личных данных'''


def send_message_with_pd(update: Update, rent_description):
    print(rent_description.bot_data)
    if update.message.text != static_text.reserve[0]:
        text = static_text.order_confirmation
        update.message.reply_text(
            text,
            reply_markup=make_keyboard_with_confirmation()
        )
        return SUMMARY
    user = StorageUser.objects.get(telegram_id=update.message.from_user.id)
    if user.there_is_pd:
        text = static_text.personal_data_from_bd.format(
            last_name=user.last_name,
            first_name=user.first_name,
            middle_name=user.middle_name,
            phone_number=user.phone_number,
            dul_s=user.DUL_series,
            dul_n=user.DUL_number,
            birthdate=user.birth_date.strftime('%d.%m.%Y')
        )
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_skip_change_pd()
        )
        return SELECT_PD
    else:
        text = static_text.request_consent
        with open(CONSENT_PD_FILEPATH, 'rb') as consent_file:
            update.message.reply_document(
                document=consent_file,
                caption=text,
                reply_markup=make_keyboard_with_consent()
            )
        return CONSENT


def get_action_with_pd(update: Update, _):
    if update.message.text == static_text.skip_change_pd[0]:
        text = static_text.pay_request
        update.message.reply_text(text=text,
                                  reply_markup=make_keyboard_with_invoice())
        return PAY
    elif update.message.text == static_text.skip_change_pd[1]:
        text = static_text.request_consent
        with open(CONSENT_PD_FILEPATH, 'rb') as consent_file:
            update.message.reply_document(
                document=consent_file,
                caption=text,
                reply_markup=make_keyboard_with_consent()
            )
        return CONSENT
    else:
        text = static_text.personal_data_from_bd_short
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_skip_change_pd()
        )
        return SELECT_PD


def get_user_consent(update: Update, _):
    if update.message.text == static_text.consent_button[1]:
        text = static_text.request_consent_again
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_consent()
        )
        return CONSENT
    elif update.message.text == static_text.consent_button[0]:
        text = static_text.request_fio
        update.message.reply_text(
            text=text
        )
        return FIO
    else:
        text = static_text.request_consent
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_with_consent()
        )
        return CONSENT


def get_fio(update: Update, user_pd):
    fio = update.message.text
    try:
        last_name, first_name, middle_name = map(
            lambda x: x.title(), fio.split()
        )
    except ValueError:
        text = static_text.request_fio_again
        update.message.reply_text(
            text=text
        )
        return FIO
    user_pd.bot_data['first_name'] = first_name
    user_pd.bot_data['middle_name'] = middle_name
    user_pd.bot_data['last_name'] = last_name

    text = static_text.request_contact
    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_to_get_contact()
    )
    return PHONE


def get_contact(update: Update, user_pd):
    try:
        phone_number = update.message.contact.phone_number
    except AttributeError:
        phone_number = update.message.text
    phonenumber = phone_number.replace('+', '').replace('-', '')
    if not phonenumber.isdigit() or len(phonenumber) < 11:
        text = static_text.request_contact
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_to_get_contact()
        )
        return PHONE
    pure_phonenumber = phonenumbers.parse(phonenumber, 'RU')
    if phonenumbers.is_valid_number(pure_phonenumber):
        normalize_phonenumber = phonenumbers.format_number(
            pure_phonenumber,
            phonenumbers.PhoneNumberFormat.E164
        )
        user_pd.bot_data['phone_number'] = normalize_phonenumber
    else:
        text = static_text.request_contact
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_to_get_contact()
        )
        return PHONE

    text = static_text.request_dul
    update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardRemove()
    )
    return DUL


def get_dul(update: Update, user_pd):
    dul = update.message.text
    try:
        dul_series, dul_number = dul.split()
        if len(dul_series) != 4 or len(dul_number) != 6:
            raise ValueError
    except ValueError:
        text = static_text.request_dul
        update.message.reply_text(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
        return DUL

    user_pd.bot_data['dul_series'] = dul_series
    user_pd.bot_data['dul_number'] = dul_number

    text = static_text.request_dirthdate
    update.message.reply_text(
        text=text
    )
    return BIRTHDATE


def get_birthdate(update: Update, user_pd):
    birth_date = update.message.text
    birth_date = birth_date.replace(',', '.')
    try:
        day, month, year = birth_date.split('.')
        if len(day) > 2 or len(month) > 2 or len(year) != 4:
            raise ValueError
    except ValueError:
        text = static_text.request_dirthdate
        update.message.reply_text(
            text=text
        )
        return BIRTHDATE
    user_pd.bot_data['birth_date_day'] = day
    user_pd.bot_data['birth_date_month'] = month
    user_pd.bot_data['birth_date_year'] = year
    user_pd.bot_data['telegram_id'] = update.message.from_user.id

    update_data_in_database(user_pd)

    text = static_text.pay_request
    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_with_invoice())

    return PAY


def update_data_in_database(user_pd):
    user = StorageUser.objects.get(telegram_id=user_pd.bot_data['telegram_id'])
    user.first_name = user_pd.bot_data['first_name']
    user.middle_name = user_pd.bot_data['middle_name']
    user.last_name = user_pd.bot_data['last_name']
    user.phone_number = user_pd.bot_data['phone_number']

    user.DUL_series = user_pd.bot_data['dul_series']
    user.DUL_number = user_pd.bot_data['dul_number']

    day, month, year = map(int, (
        user_pd.bot_data['birth_date_day'],
        user_pd.bot_data['birth_date_month'],
        user_pd.bot_data['birth_date_year']
    ))
    user.birth_date = date(year, month, day)

    user.there_is_pd = True

    user.save()


'''Конец сценария'''

'''Сценарий оплаты'''


def send_shipping_callback(update: Update, context: CallbackContext):
    if update.message.text == static_text.send_invoice[1]:
        text = static_text.cancel_text
        update.message.reply_text(
            text=text,
            reply_markup=make_keyboard_for_start_command(),
        )
        return ConversationHandler.END
    if update.message.text != static_text.send_invoice[0]:
        text = static_text.pay_request
        update.message.reply_text(text=text,
                                  reply_markup=make_keyboard_with_invoice())
        return PAY
    chat_id = update.message.chat_id
    title = static_text.pay_title

    period_count = context.bot_data['period_count']
    period_name = context.bot_data['period_name']
    correct_period = static_text.correct_names[f'{period_count} {period_name}']
    description = static_text.pay_description.format(
        correct_period=correct_period
    )
    # select a payload just for you to recognize its the donation from your bot
    payload = static_text.pay_payload
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    provider_token = PROVIDER_TOKEN
    currency = static_text.pay_currency

    thing = StoredThing.objects.get(
        thing_name=context.bot_data['stuff_category'])
    is_month = False if context.bot_data['period_name'] == 'неделя' else True
    if context.bot_data['category'] == 'Сезонные вещи':
        things_count = context.bot_data['stuff_count']
    else:
        things_count = context.bot_data['dimensions']

    price = int(thing.get_storage_cost(
        context.bot_data['period_count'],
        is_month,
        things_count,
        context.bot_data['promo_code']
    ))
    print(f'send_shipping_callback().price: {price}')

    prices = [LabeledPrice(currency, price * 100)]
    print(f'send_shipping_callback().prices: {prices}')
    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(
        chat_id, title, description, payload, provider_token, currency, prices
    )


# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update: Update, _) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != static_text.pay_payload:
        # answer False pre_checkout_query
        query.answer(ok=False, error_message=static_text.pay_error)
    else:
        query.answer(ok=True)


# finally, after contacting the payment provider...
def successful_payment_callback(update: Update, rent_description: CallbackContext) -> None:
    """Confirms the successful payment."""
    qr_filename = Orders.save_order(rent_description.bot_data)

    update.message.reply_text(static_text.pay_success)
    period_name = rent_description.bot_data['period_name']
    period_count = rent_description.bot_data['period_count']
    date_from = datetime.now()
    if period_name == 'неделя':
        date_to = date_from + timedelta(weeks=int(period_count))
    else:
        date_to = date_from + relativedelta(months=int(period_count))

    with open(qr_filename, 'rb') as qr_file:
        caption = static_text.qr_caption.format(
            date_from=date_from.strftime('%d.%m.%Y'),
            date_to=date_to.strftime('%d.%m.%Y')
        )
        update.message.reply_document(document=qr_file,
                                      caption=caption)
    os.remove(BASE_DIR / qr_filename)
    update.message.reply_text(static_text.rent_new,
                              reply_markup=make_keyboard_for_start_command())
    return ConversationHandler.END


'''Конец сценария оплаты'''
