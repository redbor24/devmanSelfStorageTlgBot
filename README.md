## Описание

Телеграм-бот в режиме диалога помогает оформить заказ по аренде складского 
помещения для сезонного хранения личных вещей. Например, предметов 
для зимнего или летнего отдыха, или автомобильной резины. 

### Имя бота в Telegram
```
SelfStorage
```

### Команды бота в Telegram
Запуск бота
```
/start
```
Перезапуск диалога с ботом
```
/cancel
```
Получение статистики в формате CSV
```
/admin
```

## Установка

- Скачать код
```bash
git clone https://github.com/Alex-Men-VL/self_storage.git
cd self_storage
```
- Создать виртуальное окружение

*nix или MacOS:
```bash
python3 -m venv env
source env/bin/activate
```
Windows:
```bash
python -m venv env
source env/bin/activate
```

- Установить зависимости
```bash
pip install -r requirements.txt
```
- Создать файл .env и вставить в него следующие строки:
```bash
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
TELEGRAM_TOKEN=<Токен вашего бота>
PROVIDER_TOKEN=<Токен счета вашего бота>
```
[Как получить PROVIDER_TOKEN](https://yookassa.ru/docs/support/payments/onboarding/integration/cms-module/telegram)
- Запустите миграцию для настройки базы данных SQLite:

*nix или MacOS:
```bash
python3 manage.py migrate
```
Windows:
```bash
python manage.py migrate
```
- Создайте суперпользователя, чтобы получить доступ к панели администратора:

*nix или MacOS:
```bash
python3 manage.py createsuperuser
```
Windows:
```bash
python manage.py createsuperuser
```

- Инициализация основных справочников:

*nix или MacOS:
```bash
python3 db_init.py
```
Windows:
```bash
python db_init.py
```

## Запуск бота
*nix или MacOS:
```bash
python3 run_pooling.py 
```
Windows:
```bash
python run_pooling.py 
```
## Запуск панели администратора:
*nix или MacOS:
```bash
python3 manage.py runserver
```
Windows:
```bash
python manage.py runserver
```

Затем перейдите по [ссылке](http://127.0.0.1:8000/admin/).