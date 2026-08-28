from django.db import models


class BookCategory(models.Model):
    category_id = models.BigAutoField(primary_key=True, db_column="category_id")
    category_name = models.CharField(
        max_length=50, unique=True, db_column="category_name"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column="parent_id",
        related_name="children",
    )
    sort_order = models.IntegerField(default=0, db_column="sort_order")
    status = models.CharField(max_length=20, default="ACTIVE", db_column="status")
    created_at = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "book_category"
        managed = False

    def __str__(self):
        return self.category_name


class BookCondition(models.Model):
    condition_id = models.BigAutoField(primary_key=True, db_column="condition_id")
    condition_name = models.CharField(
        max_length=50, unique=True, db_column="condition_name"
    )
    description = models.CharField(
        max_length=255, null=True, blank=True, db_column="description"
    )

    class Meta:
        db_table = "book_condition"
        managed = False

    def __str__(self):
        return self.condition_name


class Book(models.Model):
    book_id = models.BigAutoField(primary_key=True, db_column="book_id")
    category = models.ForeignKey(
        BookCategory,
        on_delete=models.DO_NOTHING,
        db_column="category_id",
        related_name="books",
    )
    title = models.CharField(max_length=200, db_column="title")
    isbn = models.CharField(max_length=20, null=True, blank=True, db_column="isbn")
    author = models.CharField(max_length=100, db_column="author")
    publisher = models.CharField(max_length=100, db_column="publisher")
    course_name = models.CharField(
        max_length=100, null=True, blank=True, db_column="course_name"
    )
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, db_column="original_price"
    )
    edition = models.CharField(max_length=50, null=True, blank=True, db_column="edition")
    publish_year = models.IntegerField(
        null=True, blank=True, db_column="publish_year"
    )
    created_at = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "book"
        managed = False

    def __str__(self):
        return self.title


class PickupPoint(models.Model):
    pickup_point_id = models.BigAutoField(
        primary_key=True, db_column="pickup_point_id"
    )
    name = models.CharField(max_length=100, unique=True, db_column="name")
    location = models.CharField(max_length=255, db_column="location")
    contact_phone = models.CharField(
        max_length=20, null=True, blank=True, db_column="contact_phone"
    )
    open_time = models.CharField(
        max_length=100, null=True, blank=True, db_column="open_time"
    )
    status = models.CharField(max_length=20, default="ACTIVE", db_column="status")
    created_at = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "pickup_point"
        managed = False

    def __str__(self):
        return self.name
