from django import forms
from .models import Measurement

class MeasurementModeForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ('destination',)