from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML, Fieldset, ButtonHolder

# Models
from .models import Exam, Word

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ExamForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields['solution'].widget.attrs['rows'] = 10
        self.fields['evaluation_text'].widget.attrs['rows'] = 10
