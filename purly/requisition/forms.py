from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import models

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

    class Media:
        js = ["admin/js/requisition_line_toggle.js"]

    def clean(self):
        cleaned_data = super().clean()
        requisition = cleaned_data.get("requisition")
        ship_to = cleaned_data.get("ship_to")

        if (
            self.instance.pk is None
            or "requisition" in self.changed_data
            or "ship_to" in self.changed_data
        ):
            if requisition and requisition.status not in [
                RequisitionStatusChoices.DRAFT,
                RequisitionStatusChoices.REJECTED,
            ]:
                raise forms.ValidationError(
                    {"requisition": "This requisition must be in draft or rejected status."}
                )

            if ship_to and ship_to.deleted:
                raise forms.ValidationError({"ship_to": "This address was deleted."})

        return cleaned_data


class RequisitionLineInlineFormSet(models.BaseInlineFormSet):
    def clean(self):
        super().clean()

        line_numbers = []
        forms = []

        total_lines = 0
        total_deleted = 0

        for form in self.forms:
            if form.instance.pk or form.has_changed():
                total_lines += 1

            deleted = form.cleaned_data.get("DELETE")

            if deleted:
                total_deleted += 1

            line_number = form.cleaned_data.get("line_number")

            if not deleted and line_number is not None:
                line_numbers.append(line_number)
                forms.append(form)

        if total_deleted > 0 and total_deleted == total_lines:
            raise ValidationError("Ensure at least one line is present before deleting.")

        if total_lines > settings.MAX_REQUISITION_LINES:
            raise ValidationError("Ensure only 250 or less lines are provided.")

        if len(line_numbers) > len(set(line_numbers)):
            for form in forms:
                form.add_error(
                    "line_number", ValidationError("Line numbers must contain unique values.")
                )
