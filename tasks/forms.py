from django import forms
from datetime import date, datetime
from .models import ForceMember, PresentAddress, PermanentAddress, MiRoomVisit, Duty, Ro

current_year = date.today().year

# -------------------------------
# 🔹 Style Mixin
# -------------------------------
class StyleFormMixin:
    base_classes = "border-blue-500 focus:ring-2 focus:ring-blue-300 rounded-md py-1 px-2"

    default_classes = {
        "input": f"form-input {base_classes}",
        "select": f"form-select {base_classes}",
        "checkbox": "form-checkbox h-5 w-5 text-blue-500",
    }

    def apply_style_widgets(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.FileInput)):
                widget.attrs.setdefault('class', self.default_classes['input'])
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', self.default_classes['select'])
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', self.default_classes['checkbox'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_widgets()


# -------------------------------
# 🔹 ForceMember Form
# -------------------------------
class ForceModelForm(StyleFormMixin, forms.ModelForm):

    svc_join = forms.CharField(
        required=False,
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y"),
        widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY'})
    )
    rab_join = forms.CharField(
        required=False,
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y"),
        widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY'})
    )
    birth_day = forms.CharField(
        required=False,
        initial=date(current_year, 1, 1).strftime("%d/%m/%Y"),
        widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY'})
    )

    class Meta:
        model = ForceMember
        exclude = ['company']
        fields = [
            'no','name','rank','force','svc_join','mother_unit',
            'rab_join','birth_day','nid','email','phone','photo',
            'wf_phone','company'
        ]

    def _clean_date(self, field):
        data = self.cleaned_data.get(field)
        if data:
            try:
                return datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError("Use DD/MM/YYYY format")
        return None

    def clean_svc_join(self):
        return self._clean_date('svc_join')

    def clean_rab_join(self):
        return self._clean_date('rab_join')

    def clean_birth_day(self):
        return self._clean_date('birth_day')


# -------------------------------
# 🔹 Present Address Form
# -------------------------------
class PresentModelForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = PresentAddress
        fields = ['house','road','sector','village','post','thana','district','division']


# -------------------------------
# 🔹 Permanent Address Form
# -------------------------------
class PermanentModelForm(StyleFormMixin, forms.ModelForm):
    same_as_present = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': StyleFormMixin.default_classes['checkbox']})
    )

    class Meta:
        model = PermanentAddress
        fields = ['house','road','sector','village','post','thana','district','division']


# -------------------------------
# 🔹 Company Assign Form
# -------------------------------
class CompanySelectForm(forms.ModelForm):
    class Meta:
        model = ForceMember
        fields = ['company']


# -------------------------------
# 🔹 Duty Form
# -------------------------------
class DutyForm(forms.ModelForm):

    member_numbers = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "101, 102\nঅথবা\n101\n102",
            "class": "border border-blue-600 rounded p-2 w-3/4"
        })
    )

    member_no = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'border-2 border-blue-600 rounded p-2 w-3/4',
            'placeholder': 'Member No'
        })
    )

    members = forms.ModelMultipleChoiceField(
        queryset=ForceMember.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'border border-blue-400 rounded p-2 w-full h-40'
        })
    )

    class Meta:
        model = Duty
        fields = [
            'serial_no','member_numbers','member_no','members',
            'date','start_time','end_time','destination','signature'
        ]
        widgets = {
            'serial_no': forms.TextInput(attrs={'readonly': True,'class': 'bg-gray-100'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'destination': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['signature'].disabled = True


# -------------------------------
# 🔹 Mi Room Visit Form
# -------------------------------
class MiRoomVisitForm(forms.ModelForm):
    per_number = forms.IntegerField(label="Per Number")

    class Meta:
        model = MiRoomVisit
        fields = ['per_number','symptoms','treatment']

    def clean_per_number(self):
        per_no = self.cleaned_data['per_number']
        try:
            return ForceMember.objects.get(no=per_no)
        except ForceMember.DoesNotExist:
            raise forms.ValidationError("Invalid Per Number")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.member = self.cleaned_data['per_number']
        if commit:
            instance.save()
        return instance


# -------------------------------
# 🔹 Ro Form
# -------------------------------
class RoForm(forms.ModelForm):
    class Meta:
        model = Ro
        fields = ['member','destination','sing']
