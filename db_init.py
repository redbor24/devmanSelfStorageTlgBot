import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'self_storage.settings')
django.setup()

from tgbot.models import StoredThing, Storage
from db_constants import (
    storages,
    stored_things,
)


def init():
    for city, address in storages.items():
        Storage.objects.get_or_create(
            storage_name=city,
            storage_address=address
        )

    for name, property in stored_things.items():
        StoredThing.objects.get_or_create(
            thing_name=name,
            seasonal=property['seasonal'],
            tariff1=property['tariff1'],
            tariff2=property['tariff2']
        )


if __name__ == '__main__':
    init()
