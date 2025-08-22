from django import forms

from .models import Requisition, RequisitionLine, RequisitionStatusChoices


class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        owner = cleaned_data.get("owner")
        project = cleaned_data.get("project")

        if (
            self.instance.pk is None
            or "owner" in self.changed_data
            or "project" in self.changed_data
        ):
            if owner and not owner.is_active:
                raise forms.ValidationError({"owner": "This account must be active."})

            if project and project.deleted:
                raise forms.ValidationError({"project": "This project was deleted."})

        return cleaned_data


class RequisitionLineForm(forms.ModelForm):
    class Meta:
        model = RequisitionLine
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        requisition = cleaned_data.get("requisition")
        ship_to = cleaned_data.get("ship_to")

        if (
            self.instance.pk is None
            or "requisition" in self.changed_data
            or "ship_to" in self.changed_data
        ):
            if requisition and requisition.status != RequisitionStatusChoices.DRAFT:
                raise forms.ValidationError(
                    {"requisition": "This requisition must be in draft status."}
                )

            if ship_to and ship_to.deleted:
                raise forms.ValidationError({"ship_to": "This address was deleted."})

        return cleaned_data
