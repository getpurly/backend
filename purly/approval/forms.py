import re

from django import forms
from django.core.exceptions import ValidationError

from .models import ApprovalChainHeaderRule, ApprovalChainLineRule, OperatorChoices


class ApprovalChainRuleForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        operator = cleaned_data.get("operator")
        value = cleaned_data.get("value")

        if operator != OperatorChoices.IS_NULL and not value:
            raise ValidationError({"value": "This field is required."})

        if operator == OperatorChoices.IS_NULL and value:
            value.pop()

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
        help_texts = {"value": "This field is required unless operator is isnull."}


class ApprovalChainLineRuleForm(ApprovalChainRuleForm):
    class Meta(ApprovalChainRuleForm.Meta):
        model = ApprovalChainLineRule
        help_texts = {
            "value": "This field is required unless operator is isnull.",
            "match_mode": "Select whether to match all lines or any line.",
        }
