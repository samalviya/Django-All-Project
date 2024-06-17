# forms.py
from django import forms

class GeoTIFFForm(forms.Form):
    bbox = forms.CharField(
        label='Bounding Box',
        help_text='Enter bounding box as lat,long, lat,long',
        initial='75.87039459422876,22.72440827407615,75.8712162352702,22.72387051478303',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter bounding box diagonals coordinates',
            'data-toggle': 'tooltip',
            'title': 'Format: west,south,east,north','style': 'color: black;'  
        })
    )
    zoom = forms.IntegerField(
        label='Zoom Level',
        help_text='Enter the zoom level',
        initial=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter zoom level',
            'data-toggle': 'tooltip',
            'title': 'A number between 17 to 22'
        })
    )
