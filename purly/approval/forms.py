import re
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError

from .models import (
    ApprovalChain,
    ApprovalChainHeaderRule,
    ApprovalChainLineRule,
    ApprovalChainModeChoices,
    HeaderFieldStringChoices,
    LineFieldNumberChoices,
    LineFieldStringChoices,
    LookupNumberChoices,
    LookupStringChoices,
)


class ApprovalChainForm(forms.ModelForm):
    class Meta:
        model = ApprovalChain
        fields = "__all__"

    class Media:
        js = ["admin/js/approver_mode_toggle.js"]

    def clean(self):
        cleaned_data = super().clean()
        approver_mode = cleaned_data.get("approver_mode")
        approver = cleaned_data.get("approver")
        approver_group = cleaned_data.get("approver_group")

        if approver_mode == ApprovalChainModeChoices.INDIVIDUAL and not approver:
            raise ValidationError({"approver": "This field is required."})

        if approver_mode == ApprovalChainModeChoices.GROUP and not approver_group:
            raise ValidationError({"approver_group": "This field is required."})

        return cleaned_data

    def save(self, commit):  # type: ignore
        instance = super().save(commit)

        if instance.approver_mode == ApprovalChainModeChoices.INDIVIDUAL:
            instance.approver_group = None
        else:
            instance.approver = None

        return instance


class CommaSeparatedArrayWidget(forms.TextInput):
    def format_value(self, value):
        if value is not None:
            value = value.split(",")

            return ", ".join(value)

        return value


class ApprovalChainRuleForm(forms.ModelForm):
    value = SimpleArrayField(
        base_field=forms.CharField(), required=False, widget=CommaSeparatedArrayWidget
    )

    class Meta:
        fields = "__all__"

    class Media:
        js = ["admin/js/isnull_toggle.js"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["lookup"].widget.attrs.update({"class": "lookup-select"})

    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get("field")
        lookup = cleaned_data.get("lookup")
        value = cleaned_data.get("value")

        if lookup != LookupStringChoices.IS_NULL and not value:
            raise ValidationError({"value": "This field is required."})

        if (
            value
            and lookup in LookupStringChoices
            and value
            and (field not in HeaderFieldStringChoices and field not in LineFieldStringChoices)
        ):
            raise ValidationError("Using a string lookup on a number field is not valid.")

        if value and lookup in LookupNumberChoices and field not in LineFieldNumberChoices:
            raise ValidationError("Using a number lookup on a string field is not valid.")

        if lookup in LookupNumberChoices:
            if len(value) > 1:  # type: ignore
                raise ValidationError({"value": "This field must contain only one number."})

            try:
                Decimal(value[0])  # type: ignore
            except InvalidOperation as e:
                raise ValidationError({"value": "This field must contain a number."}) from e

        if lookup == LookupStringChoices.REGEX and value:
            for pattern in value:
                try:
                    re.compile(pattern)  # type: ignore
                except re.error as e:
                    raise ValidationError(
                        {"value": f"There was an error with regex pattern: {e}."}
                    ) from e

        return cleaned_data

    def save(self, commit):  # type: ignore
        instance = super().save(commit)

        if instance.lookup == LookupStringChoices.IS_NULL:
            instance.value = []

        return instance


class ApprovalChainHeaderRuleForm(ApprovalChainRuleForm):
    class Meta(ApprovalChainRuleForm.Meta):
        model = ApprovalChainHeaderRule
        help_texts = {"value": "Use commas to separate multiple values."}


class ApprovalChainLineRuleForm(ApprovalChainRuleForm):
    class Meta(ApprovalChainRuleForm.Meta):
        model = ApprovalChainLineRule
        help_texts = {
            "value": "Use commas to separate multiple values.",
            "match_mode": "Select whether to match all lines or any line.",
        }
