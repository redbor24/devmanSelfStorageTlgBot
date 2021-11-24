from django.db import models
from django.utils import timezone
import qrcode


class StorageUser(models.Model):
    telegram_id = models.IntegerField(unique=True)
    username = models.CharField(
        max_length=64,
        null=True,
        blank=False,
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=256,
        null=True,
        blank=False,
        verbose_name='Имя'
    )
    middle_name = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name='Отчество'
    )
    last_name = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name='Фамилия'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Телефон (+код xxx xxx-xx-xx)'
    )
    DUL_series = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name='Серия паспорта'
    )
    DUL_number = models.CharField(
        max_length=6,
        null=True,
        blank=True,
        verbose_name='Номер паспорта'
    )
    there_is_pd = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Есть ли личные данные'
    )
    is_admin = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name='Администратор'
    )

    def __str__(self):
        if self.username:
            return f'@{self.username}'
        else:
            return f'{self.telegram_id}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Storage(models.Model):
    """
    Справочник складов с наименованием и адресом
    """
    storage_name = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Наименование')
    storage_address = models.CharField(
        max_length=1024,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Адрес')

    def __str__(self):
        if self.storage_name:
            return f'{self.storage_name}'
        else:
            return f'{self.id}'

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class StoredThing(models.Model):
    """
    Справочник хранимых вещей
    """
    thing_name = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Название вещи'
    )
    seasonal = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Сезонная вещь'
    )
    tariff1 = models.IntegerField(
        null=False,
        default=0,
        verbose_name='Цена хранения за неделю/Первый кв. метр'
    )
    tariff2 = models.IntegerField(
        null=False,
        default=0,
        verbose_name='Цена хранения за месяц/Дельта за следующие кв. метры'
    )
    from_month = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Можно хранить меньше месяца')

    def __str__(self):
        if self.thing_name:
            return f'{self.thing_name}'
        else:
            return f'{self.id}'

    def get_storage_tariff(self):
        cost = {}
        if self.tariff1 > 0:
            cost['tariff1'] = self.tariff1
        if self.tariff2 > 0:
            cost['tariff2'] = self.tariff2
        return cost

    def get_storage_cost(
        self,
        duration: int,
        is_month: bool,
        count: int,
        promo: str
    ):
        """
        Вычисление стоимости хранения.

        duration: int - длительность хранения, единиц
        is_month: bool - единица длительности хранения:
            True - месяц;
            False - неделя
        count: int - количество:
            if self.seasonal - штук сезонных вещей
            else - кв. метров
        """
        if self.seasonal:
            if is_month:
                cost = int(duration) * self.tariff2 * int(count)
            else:
                cost = int(duration) * self.tariff1 * int(count)
        else:
            if int(count) > 1:
                cost = self.tariff1 * int(duration) + \
                       self.tariff2 * (int(count) - 1) * int(duration)
            else:
                cost = self.tariff1 * int(duration)

        if promo == 'storage2022' and int(duration) >= 4 and is_month:
            return cost * 0.8
        if promo == 'storage15' and int(duration) <= 4 and not is_month:
            return cost * 0.85
        return cost

    class Meta:
        verbose_name = 'Хранимая вещь'
        verbose_name_plural = 'Хранимые вещи'


PERIOD_TYPE = [('0', 'неделя'), ('1', 'месяц')]


class Orders(models.Model):
    """
    Справочник заказов
    """
    order_num = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
        default='1',
        verbose_name='Номер заказа')
    order_date = models.DateField(
        null=False,
        default=timezone.now,
        verbose_name='Дата заказа')
    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
        default=None,
        related_name='orders',
        verbose_name='Склад')
    user = models.ForeignKey(
        StorageUser,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь')
    seasonal_store = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Сезонные вещи/другое')
    thing = models.ForeignKey(
        StoredThing,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Хранимая вещь')
    other_type_size = models.IntegerField(
        null=True,
        default=0,
        verbose_name='Габаритность ячейки')
    seasonal_things_count = models.IntegerField(
        null=True,
        verbose_name='Количество сезонных вещей')
    store_duration = models.IntegerField(
        null=True,
        verbose_name='Длительность хранения')
    store_duration_type = models.CharField(
        max_length=1,
        choices=PERIOD_TYPE,
        default='0',
        verbose_name='Единица длительности хранения')
    summa = models.FloatField(
        null=False,
        default=0,
        verbose_name='Стоимость хранения')

    def __str__(self):
        return self.get_order_num(self.id, self.user)

    @staticmethod
    def get_order_num(order_id, user):
        return f'{order_id}-{user.telegram_id}-' \
               f'{timezone.now().strftime("%Y%m%d%H%M%S")}'

    def create_qr_code(self):
        data = self.get_order_num(self.id, self.user)
        filename = f'{data}.png'
        qrcode.make(data).save(filename)
        return filename

    @classmethod
    def save_order(cls, order_values):
        seasonal_things_count = 0
        other_type_size = 0
        is_month = '1' if order_values['period_name'] == 'месяц' else '0'
        is_seasonal = True if order_values['category'] == 'Сезонные вещи' else \
            False

        if is_seasonal:
            thing = StoredThing.objects.get(
                thing_name=order_values['stuff_category'])
            seasonal_things_count = int(order_values['stuff_count'])
        else:
            thing = StoredThing.objects.get(thing_name=order_values['category'])
            other_type_size = int(order_values['dimensions'])

        user = StorageUser.objects.get(
            telegram_id=order_values['user_telegram_id'])

        new_order = Orders(
            order_num=Orders.get_order_num(1, user),
            storage=Storage.objects.get(storage_name=order_values['address']),
            user=user,
            thing=thing
        )
        new_order.seasonal_store = is_seasonal
        new_order.store_duration = int(order_values['period_count'])
        new_order.store_duration_type = is_month
        new_order.seasonal_things_count = int(seasonal_things_count)
        new_order.other_type_size = int(other_type_size)
        new_order.save()
        new_order.order_num = Orders.get_order_num(new_order.id, user)
        new_order.summa = thing.get_storage_cost(
            int(order_values['period_count']),
            True if is_month == '1' else False,
            new_order.seasonal_things_count if is_seasonal else new_order.other_type_size,
            order_values['promo_code']
        )
        new_order.save()
        return new_order.create_qr_code()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
