from django import forms


class MockPaymentForm(forms.Form):
    card_number = forms.CharField(
        min_length=12,
        max_length=19,
        label="信用卡号",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入 12-19 位数字",
                "inputmode": "numeric",
                "autocomplete": "off",
                "autocapitalize": "off",
                "spellcheck": "false",
            }
        ),
    )

    def clean_card_number(self):
        value = self.cleaned_data["card_number"]
        if not value.isdigit():
            raise forms.ValidationError("信用卡号只能包含数字。")
        if not 12 <= len(value) <= 19:
            raise forms.ValidationError("信用卡号长度必须为 12-19 位。")
        return value
