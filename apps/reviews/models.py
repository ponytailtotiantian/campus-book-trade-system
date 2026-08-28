from django.conf import settings
from django.db import models

from apps.trade.models import Order


class Review(models.Model):
    review_id = models.BigAutoField(primary_key=True, db_column="review_id")
    order = models.OneToOneField(
        Order,
        on_delete=models.DO_NOTHING,
        db_column="order_id",
        related_name="review",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_column="reviewer_id",
        related_name="given_reviews",
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_column="reviewee_id",
        related_name="received_reviews",
    )
    rating = models.IntegerField(db_column="rating")
    content = models.CharField(
        max_length=500, null=True, blank=True, db_column="content"
    )
    created_at = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "review"
        managed = False

    def __str__(self):
        return f"review-{self.review_id}"
