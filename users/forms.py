from django import forms
from django.contrib.auth.models import User
import re  
from tasks.forms import StyleFormMixin


class CustomRegistrationForm(StyleFormMixin, forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": StyleFormMixin.base_classes}),
        label="Username"
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": StyleFormMixin.base_classes}),
        label="First name"
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": StyleFormMixin.base_classes}),
        label="Last name"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": StyleFormMixin.base_classes}),
        label="Email address"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": StyleFormMixin.base_classes}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": StyleFormMixin.base_classes}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    # ✅ Password validation
    def clean_password(self):  # যখন Django password ফিল্ড যাচাই করবে, তখন এই ফাংশনটা চালাবে
        password = self.cleaned_data.get('password')
        errors = []  # ভুল হলে এখানে error message জমা হবে

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', password):
            errors.append("Password must include at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            errors.append("Password must include at least one lowercase letter.") 
        if not re.search(r'[0-9]', password):  # ✅ fixed regex
            errors.append("Password must include at least one number.") 
        if not re.search(r'[@#$^&!\-+=]', password):
            errors.append("Password must include at least one special character.")
        
        if errors:
            raise forms.ValidationError(errors)

        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Database-এ email আছে কিনা চেক
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("email already exists.")

        return email
    
    # ✅ Password match validation
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
