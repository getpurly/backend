import re
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError

from purly.requisition.models import RequisitionStatusChoices

from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainHeaderRule,
    ApprovalChainLineRule,
    ApprovalChainModeChoices,
    ApprovalGroup,
    HeaderFieldStringChoices,
    LineFieldNumberChoices,
    LineFieldStringChoices,
    LookupNumberChoices,
    LookupStringChoices,
)


class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        requisition = cleaned_data.get("requisition")
        approver = cleaned_data.get("approver")

        if (
            self.instance.pk is None
            or "requisition" in self.changed_data
            or "approver" in self.changed_data
        ):
            if requisition and requisition.deleted:
                raise forms.ValidationError({"requisition": "This requisition was deleted."})

            if requisition and requisition.status != RequisitionStatusChoices.PENDING_APPROVAL:
                raise forms.ValidationError(
                    {"requisition": "This requisition must be in pending status."}
                )

            if approver and not approver.is_active:
                raise forms.ValidationError({"approver": "This account must be active."})

        return cleaned_data


class ApprovalChainForm(forms.ModelForm):
    class Meta:
        model = ApprovalChain
        fields = "__all__"

    class Media:
        js = ["admin/js/approver_mode_toggle.js"]

    def clean(self):
        cleaned_data = super().clean()
        min_amount = cleaned_data.get("min_amount")
        max_amount = cleaned_data.get("max_amount")
        approver_mode = cleaned_data.get("approver_mode")
        approver = cleaned_data.get("approver")
        approver_group = cleaned_data.get("approver_group")

        if max_amount is not None and min_amount >= max_amount:
            raise ValidationError({"min_amount": "This value must be lower than maximum amount."})

        if approver_mode == ApprovalChainModeChoices.INDIVIDUAL and not approver:
            raise ValidationError({"approver": "This field is required."})

        if approver_mode == ApprovalChainModeChoices.GROUP and not approver_group:
            raise ValidationError({"approver_group": "This field is required."})

        if (
            self.instance.pk is None
            or "approver" in self.changed_data
            or "approver_group" in self.changed_data
        ):
            if (
                approver_mode == ApprovalChainModeChoices.INDIVIDUAL
                and approver
                and not approver.is_active
            ):
                raise forms.ValidationError({"approver": "This account must be active."})

            if (
                approver_mode == ApprovalChainModeChoices.GROUP
                and approver_group
                and approver_group.deleted
            ):
                raise forms.ValidationError({"approver_group": "This approval group was deleted."})

        return cleaned_data

    def save(self, commit):  # type: ignore
        instance = super().save(commit=False)

        if instance.approver_mode == ApprovalChainModeChoices.INDIVIDUAL:
            instance.approver_group = None
        else:
            instance.approver = None

        if instance.deleted:
            instance.active = False

        if commit:
            instance.save()

        return instance


class ApprovalGroupForm(forms.ModelForm):
    class Meta:
        model = ApprovalGroup
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        approvers = cleaned_data.get("approver")

        if (self.instance.pk is None or "approver" in self.changed_data) and approvers:
            for approver in approvers:
                if not approver.is_active:
                    raise forms.ValidationError(
                        {"approver": f"This account {approver} must be active."}
                    )

        return cleaned_data


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
        approval_chain = cleaned_data.get("approval_chain")
        field = cleaned_data.get("field")
        lookup = cleaned_data.get("lookup")
        value = cleaned_data.get("value")

        if lookup != LookupStringChoices.IS_NULL and not value:
            raise ValidationError({"value": "This field is required."})

        if (
            value
            and lookup in LookupStringChoices
            and (field not in HeaderFieldStringChoices and field not in LineFieldStringChoices)
        ):
            raise ValidationError(
                {
                    "field": "Using a string lookup on a number field is not valid.",
                    "lookup": "Using a string lookup on a number field is not valid.",
                }
            )

        if value and lookup in LookupNumberChoices and field not in LineFieldNumberChoices:
            raise ValidationError(
                {
                    "field": "Using a number lookup on a string field is not valid.",
                    "lookup": "Using a number lookup on a string field is not valid.",
                }
            )

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
                    re.compile(pattern)
                except re.error as e:
                    raise ValidationError(
                        {"value": f"There was an error with regex pattern: {e}."}
                    ) from e

        if self.instance.pk is None or "approval_chain" in self.changed_data:
            if approval_chain and approval_chain.deleted:
                raise forms.ValidationError({"approval_chain": "This approval chain was deleted."})

            if approval_chain and not approval_chain.active:
                raise forms.ValidationError(
                    {"approval_chain": "This approval chain must be active."}
                )

        return cleaned_data

    def save(self, commit):  # type: ignore
        instance = super().save(commit=False)

        if instance.lookup == LookupStringChoices.IS_NULL:
            instance.value = []

        if commit:
            instance.save()

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
