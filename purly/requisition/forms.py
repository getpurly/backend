from decimal import Decimal

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import models
from django.utils import timezone

from .models import LineTypeChoices, Requisition, RequisitionLine


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
                self.add_error("owner", "This account was deactivated.")

            if project and project.deleted:
                self.add_error("project", "This project was deleted.")

        return cleaned_data


class RequisitionLineForm(forms.ModelForm):
    class Meta:
        model = RequisitionLine
        fields = "__all__"

    class Media:
        js = ["admin/js/line_type_toggle.js"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["line_type"].widget.attrs.update({"class": "line_type-select"})

    def clean(self):
        cleaned_data = super().clean()
        line_type = cleaned_data.get("line_type")
        quantity = cleaned_data.get("quantity")
        unit_of_measure = cleaned_data.get("unit_of_measure")
        unit_price = cleaned_data.get("unit_price")
        line_total = cleaned_data.get("line_total")
        need_by = cleaned_data.get("need_by")
        ship_to = cleaned_data.get("ship_to")

        if (
            (self.instance.pk is None or "ship_to" in self.changed_data)
            and ship_to
            and ship_to.deleted
        ):
            self.add_error("ship_to", "This address was deleted.")

        if line_type and line_type == LineTypeChoices.GOODS:
            if not quantity:
                self.add_error("quantity", "This field is required.")

            if not unit_of_measure:
                self.add_error("unit_of_measure", "This field is required.")

            if not unit_price:
                self.add_error("unit_price", "This field is required.")

        if line_type and line_type == LineTypeChoices.SERVICE and not line_total:
            self.add_error("line_total", "This field is required.")

        if need_by and need_by < timezone.now().date():
            self.add_error("need_by", "This must be a future date.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.line_type == LineTypeChoices.GOODS:
            instance.line_total = Decimal(instance.quantity) * Decimal(instance.unit_price)

        if instance.line_type == LineTypeChoices.SERVICE:
            instance.quantity = None
            instance.unit_of_measure = ""
            instance.unit_price = None

        if commit:
            instance.save()

        return instance


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
