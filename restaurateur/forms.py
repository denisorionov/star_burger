from django import forms
from django.forms import formset_factory, modelform_factory, modelformset_factory

from foodcartapp.models import Order, OrderItem

STATUS_CHOICES = [
    ('pending', 'необработанный'),
    ('processed', 'обработанный')
]

PAYMENT_TYPE = [
    ('electronic', 'электронно'),
    ('cash', 'наличными при получении')
]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'address', 'phonenumber', 'status', 'comment', 'payment_type']

        widgets = {
            'id': forms.TextInput(attrs={'class': 'text', 'size': '1', 'readonly': 'readonly'}),
            'firstname': forms.TextInput(attrs={'class': 'text', 'size': '4'}),
            'lastname': forms.TextInput(attrs={'class': 'text', 'size': '4'}),
            'status': forms.Select(attrs={'class': "select"}, choices=STATUS_CHOICES),
            'address': forms.TextInput(attrs={'class': 'text', 'size': '10'}),
            'phonenumber': forms.TextInput(attrs={'class': 'text', 'size': '8'}),
            'comment': forms.TextInput(attrs={'class': 'text', 'size': '10'}),
            'payment_type': forms.Select(attrs={'class': 'select'}, choices=PAYMENT_TYPE),
        }


OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
