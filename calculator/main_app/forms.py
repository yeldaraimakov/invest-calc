from django import forms

from .models import User


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(max_length=255, required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=255, required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        user = User.objects.filter(email=email).first()

        if user:
            raise forms.ValidationError('Эта почта уже зарегистрирована')

        return email

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and len(password1) < 6:
            raise forms.ValidationError('Длина пароля слишком мала')

        if password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')

    def save(self, commit=True):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        password1 = self.cleaned_data.get('password1')

        user = User.objects.create_investor(first_name=first_name, last_name=last_name,
                                            email=email, password=password1)

        if commit:
            user.save()
        return user
