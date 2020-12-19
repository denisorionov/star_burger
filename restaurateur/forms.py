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
            'firstname': forms.TextInput(attrs={'class': 'text', 'size': '4', 'required': True}),
            'lastname': forms.TextInput(attrs={'class': 'text', 'size': '4', 'required': True}),
            'status': forms.Select(attrs={'class': "select"}, choices=STATUS_CHOICES),
            'address': forms.TextInput(attrs={'class': 'text', 'size': '10', 'required': True}),
            'phonenumber': forms.TextInput(attrs={'class': 'text', 'size': '8', 'required': True}),
            'comment': forms.TextInput(attrs={'class': 'text', 'size': '10'}),
            'payment_type': forms.Select(attrs={'class': 'select'}, choices=PAYMENT_TYPE),
        }

    def clean_firstname(self):
        firstname = self.cleaned_data.get('firstname')
        if firstname.isalpha():
            return firstname
        else:
            raise forms.ValidationError("Имя должно состоять только из букв")

    def clean_lastname(self):
        lastname = self.cleaned_data.get('lastname')
        if lastname.isalpha():
            return lastname
        else:
            raise forms.ValidationError("Фамилия должна состоять только из букв")


OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
