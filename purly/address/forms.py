from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        owner = cleaned_data.get("owner")

        if (
            (self.instance.pk is None or "owner" in self.changed_data)
            and owner
            and not owner.is_active
        ):
            raise forms.ValidationError({"owner": "This account must be active."})

        return cleaned_data
