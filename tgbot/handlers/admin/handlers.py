from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from self_storage.settings import ADMIN_PASSWORD
from tgbot.models import StorageUser, Orders, Storage
from tgbot.handlers.admin import static_text
from .keyboard_utils import make_keyboard_with_admin_features
from .utils import _get_csv_from_qs_values


def command_admin(update: Update, _):
    user = StorageUser.objects.get(telegram_id=update.message.from_user.id)
    if not user.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return ConversationHandler.END
    text = static_text.admin_features

    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_with_admin_features())


def send_orders_statistics(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    orders = Orders.objects.all().values()
    csv_orders = _get_csv_from_qs_values(orders, 'Аренды')
    context.bot.send_document(chat_id=query.from_user.id, document=csv_orders)

    users = StorageUser.objects.all().values()
    csv_orders = _get_csv_from_qs_values(users, 'Пользователи')
    context.bot.send_document(chat_id=query.from_user.id, document=csv_orders)

    storage = Storage.objects.all().values()
    csv_storage = _get_csv_from_qs_values(storage, 'Склады')
    context.bot.send_document(chat_id=query.from_user.id, document=csv_storage)
