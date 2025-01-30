from django import forms

class CompressionForm(forms.Form):
    compression_method = forms.ChoiceField(
        choices=[
            ('run_length', 'Run-Length Encoding'),
            ('delta', 'Delta Compression')
        ],
        widget=forms.RadioSelect,
        label="Select Compression Method"
    )
    file = forms.FileField(label="Upload Sequence File")
    reference_file = forms.FileField(
        label="Upload Reference File (for Delta Compression)",
        required=False
    )