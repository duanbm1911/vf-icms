from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import auth
from django import forms
import re


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "groups",
            "is_staff",
            "is_active",
            "password1",
            "password2",
        ]


class ValidatingPasswordChangeForm(auth.forms.PasswordChangeForm):
    MIN_LENGTH = 8

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")

        if len(password1) < self.MIN_LENGTH:
            raise forms.ValidationError(
                "The new password must be at least %d characters long."
                % self.MIN_LENGTH
            )

        first_isalpha = password1[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password1):
            raise forms.ValidationError(
                "The new password must contain at least one letter and at least one digit or"
                " punctuation character."
            )
        uppercase_error = re.search(r"[A-Z]", password1)
        if uppercase_error is None:
            raise forms.ValidationError(
                "The new password must contain at least one upper characters"
            )

        symbol_error = re.search(r"[ @!#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password1)
        if symbol_error is None:
            raise forms.ValidationError(
                "The new password must contain at least one symbol characters"
            )
        return password1

class UserSelectForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Select User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    
class EditUserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="New Password (leave blank to keep current password)"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'groups', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        groups = self.cleaned_data.get('groups')
        if password:
            user.set_password(password)
            user.save()
        if groups:
            self.save_m2m()
        return user