from django import forms

class SequenceForm(forms.Form):
    file = forms.FileField(label="Upload Sequence File")
    reference_file = forms.FileField(
        label="Upload File",
        required=False
    )