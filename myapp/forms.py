# forms.py
from django import forms

class GeoTIFFForm(forms.Form):
    bbox = forms.CharField(label='Bounding Box', help_text='Enter bounding box as west,south,east,north')
    zoom = forms.IntegerField(label='Zoom Level 20')
