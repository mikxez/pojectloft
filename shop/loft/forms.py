from django import forms
from django_svg_image_form_field import SvgAndImageFormField
from .models import Category, Customer, ShippingAddress, Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        field_classes = {
            'icon': SvgAndImageFormField
        }


# Форма для Логина
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


# Форма для заполнения данных покупателя
class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'telegram']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Имя получателя',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Фамилия получателя'
            }),

            'telegram': forms.TextInput(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Телеграм получателя'
            })
        }


class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('region', 'city', 'address', 'phone', 'comment')
        widgets = {
            'region': forms.Select(attrs={
                'class': 'contact__section-input',
            }),
            'city': forms.Select(attrs={
                'class': 'contact__section-input',
            }),

            'address': forms.TextInput(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Адрес (ул. дом. кв)'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Номер телефона',
                'type': 'phone'
            }),

            'comment': forms.Textarea(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Комментарий к заказу',
            })

        }

class EditAccountForm(UserChangeForm):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    email = forms.EmailField(required=False ,widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class EditProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    street = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    home = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    flat = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    class Meta:
        model = Profile
        fields = ('phone', 'city', 'street', 'home', 'flat')














