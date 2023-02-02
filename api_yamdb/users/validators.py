from rest_framework import serializers


class SelfValidate:

    def __init__(self, fields):
        self.fields = fields

    def __call__(self, value):
        if value['username'].lower() == 'me':
            raise serializers.ValidationError('Нельзя использовать имя "me"')
        return value
