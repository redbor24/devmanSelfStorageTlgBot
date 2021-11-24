import io
import csv

from datetime import datetime
from django.db.models import QuerySet
from typing import Dict


def _get_csv_from_qs_values(queryset: QuerySet[Dict], filename: str):
    keys = queryset[0].keys()

    s = io.StringIO()
    dict_writer = csv.DictWriter(s, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(queryset)
    s.seek(0)

    buf = io.BytesIO()

    buf.write(s.getvalue().encode())
    buf.seek(0)

    buf.name = f"{filename}__{datetime.now().strftime('%Y.%m.%d.%H.%M')}.csv"
    return buf
