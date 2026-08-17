from django import forms

from .models import (
    SurplusFood,
    Redistribution,
    Recipient
)   


# ==================================================
# SURPLUS FOOD FORM
# ==================================================

class SurplusFoodForm(forms.ModelForm):

    class Meta:

        model = SurplusFood

        fields = [
            "food_name",
            "quantity",
            "storage_temperature",
            "storage_time_hours",
        ]

        widgets = {

            "food_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter food name"
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Quantity in meals",
                    "min": "1"
                }
            ),

            "storage_temperature": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "placeholder": "Temperature in °C"
                }
            ),

            "storage_time_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "Storage time in hours"
                }
            ),
        }

    def clean_quantity(self):

        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:

            raise forms.ValidationError(
                "Quantity must be greater than 0."
            )

        return quantity

    def clean_storage_time_hours(self):

        hours = self.cleaned_data[
            "storage_time_hours"
        ]

        if hours < 0:

            raise forms.ValidationError(
                "Storage time cannot be negative."
            )

        return hours


# ==================================================
# REDISTRIBUTION FORM
# ==================================================

class RedistributionForm(forms.ModelForm):

    class Meta:

        model = Redistribution

        fields = [
            "quantity",
            "recipient",
        ]

        widgets = {

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Quantity to redistribute",
                    "min": "1"
                }
            ),

            "recipient": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )

        # ------------------------------------------
        # Show only verified recipients
        # ------------------------------------------

        self.fields[
            "recipient"
        ].queryset = Recipient.objects.filter(
            verified=True
        )

        self.fields[
            "recipient"
        ].empty_label = "Select a recipient"

    def clean_quantity(self):

        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:

            raise forms.ValidationError(
                "Redistribution quantity must be greater than 0."
            )

        return quantity

