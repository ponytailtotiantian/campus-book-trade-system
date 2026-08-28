from decimal import Decimal

from django import forms

from apps.catalog.models import Book, BookCategory, BookCondition


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.category_name


class ConditionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.description:
            return f"{obj.condition_name}（{obj.description}）"
        return obj.condition_name


class ListingCreateForm(forms.Form):
    category = CategoryChoiceField(
        queryset=BookCategory.objects.filter(status="ACTIVE").order_by(
            "sort_order", "category_id"
        ),
        label="图书分类",
        empty_label="请选择图书分类",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "required": True,
            }
        ),
    )
    title = forms.CharField(
        max_length=200,
        label="书名",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入完整书名",
            }
        ),
    )
    isbn = forms.CharField(
        max_length=20,
        required=False,
        label="ISBN",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "选填",
            }
        ),
    )
    author = forms.CharField(
        max_length=100,
        label="作者",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入作者姓名",
            }
        ),
    )
    publisher = forms.CharField(
        max_length=100,
        label="出版社",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入出版社名称",
            }
        ),
    )
    course_name = forms.CharField(
        max_length=100,
        required=False,
        label="课程名称",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "选填，如：数据库系统原理",
            }
        ),
    )
    original_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        label="原价",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "inputmode": "decimal",
                "placeholder": "0.00",
            }
        ),
    )
    edition = forms.CharField(
        max_length=50,
        required=False,
        label="版次",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "选填，如：第 3 版",
            }
        ),
    )
    publish_year = forms.IntegerField(
        required=False,
        min_value=1000,
        max_value=2100,
        label="出版年份",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "选填",
            }
        ),
    )
    condition = ConditionChoiceField(
        queryset=BookCondition.objects.order_by("condition_id"),
        label="图书成色",
        empty_label="请选择图书成色",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "required": True,
            }
        ),
    )
    listing_type = forms.ChoiceField(
        choices=(("SALE", "出售"), ("DONATION", "赠送")),
        label="商品类型",
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal("0.00"),
        label="价格",
    )
    stock = forms.IntegerField(
        min_value=0,
        initial=1,
        label="库存",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "step": "1",
            }
        ),
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        label="商品描述",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "简要描述书籍使用情况、笔记或出售原因等",
            }
        ),
    )
    donation_note = forms.CharField(
        max_length=255,
        required=False,
        label="赠送说明",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "填写领取条件、领取时间或联系说明",
            }
        ),
    )

    def clean_isbn(self):
        isbn = self.cleaned_data.get("isbn")
        if isbn and Book.objects.filter(isbn=isbn).exists():
            self.add_error("isbn", "该 ISBN 对应的图书已经存在。")
        return isbn or None

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get("listing_type")
        price = cleaned_data.get("price")

        if listing_type == "SALE":
            if price is None:
                self.add_error("price", "出售商品必须填写价格。")
            elif price < Decimal("0.00"):
                self.add_error("price", "出售商品价格不能小于 0。")
            cleaned_data["donation_note"] = None
        elif listing_type == "DONATION":
            cleaned_data["price"] = Decimal("0.00")

        return cleaned_data
