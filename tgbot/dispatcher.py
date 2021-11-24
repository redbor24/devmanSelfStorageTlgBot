import sys
import logging
from typing import Dict

from telegram import Bot, Update, BotCommand
from telegram.ext import (
    ConversationHandler, PreCheckoutQueryHandler, RegexHandler,
    ShippingQueryHandler, Updater,
    Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)
import telegram.error

from self_storage.settings import TELEGRAM_TOKEN, DEBUG
from tgbot.handlers.common import handlers as common_handlers
from tgbot.handlers.rent import handlers as rent_handlers
from tgbot.handlers.admin import handlers as admin_handlers


rent_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^(Выбрать адрес склада)$'),
                       rent_handlers.send_message_with_addresses)
    ],
    states={
        rent_handlers.SUMMARY: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.show_summary)
        ],
        rent_handlers.ASK_PROMO: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.ask_promo)
        ],
        rent_handlers.GET_PROMO: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_promo)
        ],

        rent_handlers.ADDRESS: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_store_address)
        ],
        rent_handlers.CATEGORY: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_category)
        ],
        rent_handlers.OTHER: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_dimension)
        ],
        rent_handlers.PERIOD: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_period)
        ],
        rent_handlers.SEASONAL: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_stuff_category)
        ],
        rent_handlers.COUNT: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_stuff_count)
        ],
        rent_handlers.PERIOD1: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_period_name)
        ],
        rent_handlers.PERIOD2: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_period_count)
        ],
        rent_handlers.PD: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.send_message_with_pd)
        ],
        rent_handlers.SELECT_PD: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_action_with_pd)
        ],
        rent_handlers.CONSENT: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_user_consent)
        ],
        rent_handlers.FIO: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_fio)
        ],
        rent_handlers.PHONE: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_contact),
            MessageHandler(Filters.contact & ~Filters.command,
                           rent_handlers.get_contact)
        ],
        rent_handlers.DUL: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_dul)
        ],
        rent_handlers.BIRTHDATE: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.get_birthdate)
        ],
        rent_handlers.PAY: [
            MessageHandler(Filters.text & ~Filters.command,
                           rent_handlers.send_shipping_callback)
        ],
    },
    fallbacks=[
        MessageHandler(Filters.successful_payment,
                       rent_handlers.successful_payment_callback),
        CommandHandler("cancel", common_handlers.command_cancel)
    ]

)


def setup_dispatcher(dp):
    dp.add_handler(rent_handler)

    dp.add_handler(CommandHandler("start", common_handlers.command_start))
    dp.add_handler(CommandHandler("cancel", common_handlers.command_cancel))

    dp.add_handler(CommandHandler("admin", admin_handlers.command_admin))
    dp.add_handler(CallbackQueryHandler(admin_handlers.send_orders_statistics))

    # Pre-checkout handler to final check
    dp.add_handler(PreCheckoutQueryHandler(rent_handlers.precheckout_callback))

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f'https://t.me/{bot_info["username"]}'

    print(f"Pooling of '{bot_link}' started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    updater.start_polling()
    updater.idle()


bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'admin': 'Get administrator rights',
            'cancel': 'Go back to the main menu',
        },
        'ru': {
            'admin': 'Получить права администратора',
            'cancel': 'Вернуться в главное меню',
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in
                langs_with_commands[language_code].items()
            ]
        )


# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
set_up_commands(bot)

n_workers = 1 if DEBUG else 4
dispatcher = setup_dispatcher(
    Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True)
)
