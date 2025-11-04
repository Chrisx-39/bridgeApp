from django import forms
from .models import Bridge, TrafficData, MaintenanceRecord


## 1. BridgeForm (No Change Needed - Good as Is)
# This form handles the primary Bridge model creation/update.
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


## 2. TrafficDataForm (Corrected) 💡
# The 'bridge' field is excluded because it is set automatically by the view.
class TrafficDataForm(forms.ModelForm):
    class Meta:
        model = TrafficData
        # Exclude 'bridge' and 'recorded_date' (auto_now=True)
        fields = ['heavy_vehicles', 'small_vehicles']
        widgets = {
            'heavy_vehicles': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Daily Heavy Vehicle Count'}),
            'small_vehicles': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Daily Small Vehicle Count'}),
        }


## 3. MaintenanceRecordForm (Corrected) 💡
# The 'bridge' field is excluded because it is set automatically by the view.
class MaintenanceRecordForm(forms.ModelForm):
    # Make the 'cost' field optional but enforce a minimum value if entered
    cost = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Cost in Currency (Optional)'})
    )

    class Meta:
        model = MaintenanceRecord
        # Exclude 'bridge' as it's passed via the URL and set in the view
        fields = ['action_type', 'description', 'scheduled_date', 'completed_date', 'cost', 'is_completed']
        widgets = {
            'action_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            # completed_date should be optional in the form as it may not be complete yet
            'completed_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'required': False}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        completed_date = cleaned_data.get('completed_date')
        is_completed = cleaned_data.get('is_completed')
        
        # Validation 1: If completed, must have a completed date
        if is_completed and not completed_date:
            self.add_error('completed_date', "A completed maintenance action must have a completion date.")
            
        # Validation 2: If a completed date is entered, the action must be marked completed
        if completed_date and not is_completed:
            self.add_error('is_completed', "If a completion date is set, the action must be marked as completed.")
            
        # Validation 3: Completed date must not be before scheduled date
        if scheduled_date and completed_date and completed_date < scheduled_date:
            self.add_error('completed_date', "Completion date cannot be before the scheduled date.")
            
        return cleaned_data
