
# -------------------------------
# Mixin
# -------------------------------
class StyleFormMixin:
    base_classes = "border-blue-500 focus:ring-2 focus:ring-blue-300 rounded-md py-1 px-2"

    default_classes = {
        "input": f"form-input {base_classes}",
        "select": f"form-select {base_classes}",
        "checkbox": "form-checkbox h-5 w-5 text-blue-500",
    }

# -------------------------------
# 🔹 ForceMember Form
# -------------------------------
class ForceModelForm(forms.ModelForm,StyleFormMixin):
    svc_join = forms.CharField(
        label='Svc Join',
        required=False,
        widget=forms.TextInput(attrs={'class': default_classes, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )
    rab_join = forms.CharField(
        label='RAB Join',
        required=False,
        widget=forms.TextInput(attrs={'class': select, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )
    birth_day = forms.CharField(
        label='Birth Day',
        required=False,
        widget=forms.TextInput(attrs={'class': checkbox, 'placeholder': 'DD/MM/YYYY'}),
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y")
    )

    class Meta:
        model = ForceMember
        exclude = ['company']
        fields = [
            'no', 'name', 'rank', 'force', 
            'svc_join','mother_unit', 'rab_join', 'birth_day',
            'nid', 'email', 'phone','photo', 'wf_phone','company',
        ]
        labels = {
            'no': 'Personal No',
            'name': 'Full Name',
            'rank': 'Rank',
            'force': 'Force',
            'mother_unit': 'moteher_unit',
            'svc_join': 'Svc Join',
            'rab_join': 'RAB Join',
            'birth_day': 'Birth Day',
            'nid': 'NID',
            'email': 'Email',
            'phone': 'Phone',
            'photo':'photo',
            'wf_phone': 'Wife Phone', 
            'company':'company',
        }
        widgets = {
            'no': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Personal Number'}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Full Name'}),
            'rank': forms.Select(attrs={'class': SELECT_CLASSES}),
            'force': forms.Select(attrs={'class': SELECT_CLASSES}),
            'mother_unit': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Unit Name....'}),
            'company': forms.Select(attrs={'class': SELECT_CLASSES}),
            'nid': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'NID'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Phone Number'}),
           'photo': forms.FileInput(attrs={'class': INPUT_CLASSES,}),
            'wf_phone': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Wife Phone Number'}),
        }

    # -------------------------------
    # Custom clean methods for DD/MM/YYYY
    # -------------------------------
    def clean_svc_join(self):
        data = self.cleaned_data['svc_join']
        if data:
            try:
                return datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError("Invalid date format. Use DD/MM/YYYY.")
        return None

    def clean_rab_join(self):
        data = self.cleaned_data['rab_join']
        if data:
            try:
                return datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError("Invalid date format. Use DD/MM/YYYY.")
        return None

    def clean_birth_day(self):
        data = self.cleaned_data['birth_day']
        if data:
            try:
                return datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError("Invalid date format. Use DD/MM/YYYY.")
        return None