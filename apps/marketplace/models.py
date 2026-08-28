from django.conf import settings
from django.db import models

from apps.catalog.models import Book, BookCondition


class Listing(models.Model):
    listing_id = models.BigAutoField(primary_key=True, db_column="listing_id")
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_column="seller_id",
        related_name="listings",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.DO_NOTHING,
        db_column="book_id",
        related_name="listings",
    )
    condition = models.ForeignKey(
        BookCondition,
        on_delete=models.DO_NOTHING,
        db_column="condition_id",
        related_name="listings",
    )
    listing_type = models.CharField(
        max_length=20, default="SALE", db_column="listing_type"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column="price")
    stock = models.IntegerField(default=1, db_column="stock")
    description = models.CharField(
        max_length=500, null=True, blank=True, db_column="description"
    )
    donation_note = models.CharField(
        max_length=255, null=True, blank=True, db_column="donation_note"
    )
    status = models.CharField(max_length=20, default="ON_SALE", db_column="status")
    published_at = models.DateTimeField(db_column="published_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "listing"
        managed = False

    def __str__(self):
        return f"listing-{self.listing_id}"


class ListingDetail(models.Model):
    listing_id = models.BigIntegerField(primary_key=True, db_column="listing_id")
    listing_type = models.CharField(max_length=20, db_column="listing_type")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="price"
    )
    stock = models.IntegerField(db_column="stock")
    listing_status = models.CharField(max_length=20, db_column="listing_status")
    donation_note = models.CharField(
        max_length=255, null=True, blank=True, db_column="donation_note"
    )
    seller_id = models.BigIntegerField(db_column="seller_id")
    seller_name = models.CharField(max_length=50, db_column="seller_name")
    seller_department = models.CharField(max_length=100, db_column="seller_department")
    book_id = models.BigIntegerField(db_column="book_id")
    title = models.CharField(max_length=200, db_column="title")
    author = models.CharField(max_length=100, db_column="author")
    publisher = models.CharField(max_length=100, db_column="publisher")
    category_name = models.CharField(max_length=50, db_column="category_name")
    condition_name = models.CharField(max_length=50, db_column="condition_name")
    published_at = models.DateTimeField(db_column="published_at")

    class Meta:
        managed = False
        db_table = "v_listing_detail"

    def __str__(self):
        return f"listing-detail-{self.listing_id}"
