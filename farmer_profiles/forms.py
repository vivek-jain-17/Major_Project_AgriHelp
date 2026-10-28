from django import forms
from django.forms import inlineformset_factory
from .models import FarmerProfile, FarmerCrop

class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = ["state", "district", "landholding_acres", "land_ownership", "farmer_category"]
        widgets = {
            "state": forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded-lg focus:ring-brand-500"}),
            "district": forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded-lg focus:ring-brand-500"}),
            "landholding_acres": forms.NumberInput(attrs={"class": "w-full px-4 py-2 border rounded-lg focus:ring-brand-500", "step": "0.01"}),
            "land_ownership": forms.Select(attrs={"class": "w-full px-4 py-2 border rounded-lg focus:ring-brand-500"}),
            "farmer_category": forms.Select(attrs={"class": "w-full px-4 py-2 border rounded-lg focus:ring-brand-500"}),
        }

class FarmerCropForm(forms.ModelForm):
    class Meta:
        model = FarmerCrop
        fields = ["crop_name", "area_acres"]
        widgets = {
            "crop_name": forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded-lg focus:ring-brand-500", "placeholder": "e.g. Wheat"}),
            "area_acres": forms.NumberInput(attrs={"class": "w-full px-4 py-2 border rounded-lg focus:ring-brand-500", "step": "0.01", "placeholder": "e.g. 2.5"}),
        }

# Allows adding multiple crops on one page
FarmerCropFormSet = inlineformset_factory(
    FarmerProfile, 
    FarmerCrop, 
    form=FarmerCropForm, 
    extra=2, 
    can_delete=True
)