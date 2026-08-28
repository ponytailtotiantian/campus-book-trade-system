from django.db import models

from apps.catalog.models import PickupPoint
from apps.trade.models import Order


class PickupRecord(models.Model):
    pickup_record_id = models.BigAutoField(
        primary_key=True, db_column="pickup_record_id"
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.DO_NOTHING,
        db_column="order_id",
        related_name="pickup_record",
    )
    pickup_point = models.ForeignKey(
        PickupPoint,
        on_delete=models.DO_NOTHING,
        db_column="pickup_point_id",
        related_name="pickup_records",
    )
    pickup_code = models.CharField(
        max_length=20, unique=True, db_column="pickup_code"
    )
    scheduled_time = models.DateTimeField(
        null=True, blank=True, db_column="scheduled_time"
    )
    picked_time = models.DateTimeField(
        null=True, blank=True, db_column="picked_time"
    )
    status = models.CharField(max_length=20, default="WAITING", db_column="status")
    created_at = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "pickup_record"
        managed = False

    def __str__(self):
        return f"pickup-{self.pickup_record_id}"


class PickupDetail(models.Model):
    pickup_record_id = models.BigIntegerField(
        primary_key=True, db_column="pickup_record_id"
    )
    pickup_code = models.CharField(max_length=20, db_column="pickup_code")
    pickup_status = models.CharField(max_length=20, db_column="pickup_status")
    scheduled_time = models.DateTimeField(
        null=True, blank=True, db_column="scheduled_time"
    )
    picked_time = models.DateTimeField(
        null=True, blank=True, db_column="picked_time"
    )
    pickup_point_name = models.CharField(
        max_length=100, db_column="pickup_point_name"
    )
    pickup_location = models.CharField(
        max_length=255, db_column="pickup_location"
    )
    order_id = models.BigIntegerField(db_column="order_id")
    order_type = models.CharField(max_length=20, db_column="order_type")
    title = models.CharField(max_length=200, db_column="title")
    buyer_name = models.CharField(max_length=50, db_column="buyer_name")

    class Meta:
        managed = False
        db_table = "v_pickup_detail"

    def __str__(self):
        return f"pickup-detail-{self.pickup_record_id}"
