from django.conf import settings
from django.db import models

from apps.marketplace.models import Listing


class Order(models.Model):
    order_id = models.BigAutoField(primary_key=True, db_column="order_id")
    listing = models.ForeignKey(
        Listing,
        on_delete=models.DO_NOTHING,
        db_column="listing_id",
        related_name="orders",
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_column="buyer_id",
        related_name="buyer_orders",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_column="seller_id",
        related_name="seller_orders",
    )
    order_type = models.CharField(
        max_length=20, default="SALE", db_column="order_type"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="total_amount"
    )
    status = models.CharField(max_length=20, default="PENDING", db_column="status")
    created_at = models.DateTimeField(db_column="created_at")
    paid_at = models.DateTimeField(null=True, blank=True, db_column="paid_at")
    completed_at = models.DateTimeField(
        null=True, blank=True, db_column="completed_at"
    )
    cancelled_at = models.DateTimeField(
        null=True, blank=True, db_column="cancelled_at"
    )
    remark = models.CharField(
        max_length=255, null=True, blank=True, db_column="remark"
    )

    class Meta:
        db_table = "orders"
        managed = False

    def __str__(self):
        return f"order-{self.order_id}"


class OrderDetail(models.Model):
    order_id = models.BigIntegerField(primary_key=True, db_column="order_id")
    order_type = models.CharField(max_length=20, db_column="order_type")
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="total_amount"
    )
    order_status = models.CharField(max_length=20, db_column="order_status")
    created_at = models.DateTimeField(db_column="created_at")
    completed_at = models.DateTimeField(
        null=True, blank=True, db_column="completed_at"
    )
    title = models.CharField(max_length=200, db_column="title")
    listing_type = models.CharField(max_length=20, db_column="listing_type")
    buyer_name = models.CharField(max_length=50, db_column="buyer_name")
    seller_name = models.CharField(max_length=50, db_column="seller_name")
    seller_department = models.CharField(
        max_length=100, db_column="seller_department"
    )

    class Meta:
        managed = False
        db_table = "v_order_detail"

    def __str__(self):
        return f"order-detail-{self.order_id}"


class AuditLog(models.Model):
    audit_log_id = models.BigAutoField(primary_key=True, db_column="audit_log_id")
    order = models.ForeignKey(
        Order,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column="order_id",
        related_name="audit_logs",
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column="operator_id",
        related_name="audit_logs",
    )
    action_type = models.CharField(max_length=50, db_column="action_type")
    action_detail = models.CharField(
        max_length=500, null=True, blank=True, db_column="action_detail"
    )
    created_at = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "audit_log"
        managed = False

    def __str__(self):
        return f"audit-{self.audit_log_id}"
