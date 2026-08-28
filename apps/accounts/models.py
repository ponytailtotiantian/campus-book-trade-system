from django.db import models


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True, db_column="user_id")
    student_no = models.CharField(max_length=20, unique=True, db_column="student_no")
    username = models.CharField(max_length=50, unique=True, db_column="username")
    password_hash = models.CharField(max_length=255, db_column="password_hash")
    real_name = models.CharField(max_length=50, db_column="real_name")
    phone = models.CharField(max_length=20, unique=True, db_column="phone")
    department = models.CharField(max_length=100, db_column="department")
    credit_score = models.IntegerField(default=100, db_column="credit_score")
    role = models.CharField(max_length=20, default="USER", db_column="role")
    status = models.CharField(max_length=20, default="ACTIVE", db_column="status")
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["student_no", "real_name", "phone", "department"]

    class Meta:
        db_table = "user"
        managed = False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.status == "ACTIVE"

    @property
    def is_staff(self):
        return self.role == "ADMIN"

    @property
    def is_superuser(self):
        return self.role == "ADMIN"

    def get_username(self):
        return self.username

    def get_user_id(self):
        return self.user_id

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password

        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password

        return check_password(raw_password, self.password_hash)

    def has_usable_password(self):
        return bool(self.password_hash)

    def get_session_auth_hash(self):
        import hashlib

        return hashlib.sha256(f"{self.user_id}:{self.password_hash}".encode()).hexdigest()

    def __str__(self):
        return self.username
