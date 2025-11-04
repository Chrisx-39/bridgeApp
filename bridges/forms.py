from django import forms
from .models import Bridge, TrafficData, MaintenanceRecord


class BridgeForm(forms.ModelForm):
    class Meta:
        model = Bridge
        fields = [
            'name', 'bridge_type', 'length', 'width', 'lanes', 
            'material', 'year_built', 'route', 'gps_coordinates',
            'deck_rating', 'girders_rating', 'piers_rating', 
            'abutment_rating', 'condition_notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Bridge 1'}),
            'bridge_type': forms.Select(attrs={'class': 'form-select'}),
            'length': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'width': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'lanes': forms.NumberInput(attrs={'class': 'form-input'}),
            'material': forms.Select(attrs={'class': 'form-select'}),
            'year_built': forms.NumberInput(attrs={'class': 'form-input'}),
            'route': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'gps_coordinates': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'deck_rating': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 5}),
            'girders_rating': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 5}),
            'piers_rating': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 5}),
            'abutment_rating': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 5}),
            'condition_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
        }


class TrafficDataForm(forms.ModelForm):
    class Meta:
        model = TrafficData
        fields = ['bridge', 'heavy_vehicles', 'small_vehicles']
        widgets = {
            'bridge': forms.Select(attrs={'class': 'form-select'}),
            'heavy_vehicles': forms.NumberInput(attrs={'class': 'form-input'}),
            'small_vehicles': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['bridge', 'action_type', 'description', 'scheduled_date', 'completed_date', 'cost', 'is_completed']
        widgets = {
            'bridge': forms.Select(attrs={'class': 'form-select'}),
            'action_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }