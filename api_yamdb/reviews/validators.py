import datetime as dt

from rest_framework.serializers import ValidationError


def validate_year_to_current(value):
    if not (value <= dt.datetime.now().year):
        raise ValidationError('Значение year вне диапазона')
    return value
