import re

from django import forms
from django.core.exceptions import ValidationError

from .models import ApprovalChainRule, OperatorChoices


class ApprovalChainRuleForm(forms.ModelForm):
    class Meta:
        model = ApprovalChainRule
        fields = "__all__"
        help_texts = {"value": "This field is required unless operator is isnull."}

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
