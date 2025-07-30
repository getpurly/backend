import re

from django import forms
from django.core.exceptions import ValidationError

from .models import (
    ApprovalChain,
    ApprovalChainHeaderRule,
    ApprovalChainLineRule,
    ApprovalChainModeChoices,
    OperatorChoices,
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


class ApprovalChainRuleForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    class Media:
        js = ["admin/js/isnull_toggle.js"]

    def clean(self):
        cleaned_data = super().clean()
        operator = cleaned_data.get("operator")
        value = cleaned_data.get("value")

        if operator != OperatorChoices.IS_NULL and not value:
            raise ValidationError({"value": "This field is required."})

        if operator == OperatorChoices.IS_NULL and value:
            value = None

        if operator == OperatorChoices.REGEX and value:
            for pattern in value:
                try:
                    re.compile(pattern)  # type: ignore
                except re.error as e:
                    raise ValidationError(
                        {"value": f"There was an error with regex pattern: {e}."}
                    ) from e

        return cleaned_data


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
