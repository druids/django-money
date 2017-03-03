# -*- coding: utf-8 -*-
from django.forms import MultiWidget, Select, TextInput, NumberInput
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.encoding import force_text

from moneyed.classes import Money

from ..settings import CURRENCY_CHOICES


__all__ = ('MoneyWidget', 'MoneyNumberInput')


class MoneyWidget(MultiWidget):

    def __init__(self, choices=CURRENCY_CHOICES, amount_widget=None, currency_widget=None, default_currency=None,
                 *args, **kwargs):
        self.default_currency = default_currency
        if not amount_widget:
            amount_widget = TextInput
        if not currency_widget:
            currency_widget = Select(choices=choices)
        widgets = (amount_widget, currency_widget)
        super(MoneyWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value is not None:
            return [value.amount, value.currency]
        return [None, self.default_currency]

    # Needed for Django 1.5.x, where Field doesn't have the '_has_changed' method.
    # But it mustn't run on Django 1.6, where it doesn't work and isn't needed.

    if hasattr(TextInput, '_has_changed'):  # noqa
        # This is a reimplementation of the MoneyField.has_changed,
        # but for the widget.
        def _has_changed(self, initial, data):
            if initial is None:
                initial = ['' for x in range(0, len(data))]
            else:
                if not isinstance(initial, list):
                    initial = self.decompress(initial)

            amount_widget, currency_widget = self.widgets
            amount_initial, currency_initial = initial

            try:
                amount_data = data[0]
            except IndexError:
                amount_data = None

            if amount_widget._has_changed(amount_initial, amount_data):
                return True

            try:
                currency_data = data[1]
            except IndexError:
                currency_data = None

            if currency_widget._has_changed(currency_initial, currency_data) and amount_data:
                return True

            return False


class MoneyNumberInput(NumberInput):

    def render(self, name, value, attrs=None):
        if isinstance(value, Money):
            value = value.amount

        return super(MoneyNumberInput, self).render(name, value, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        value = super(MoneyNumberInput, self).value_from_datadict(data, files, name)
        return value.amount if isinstance(value, Money) else value
