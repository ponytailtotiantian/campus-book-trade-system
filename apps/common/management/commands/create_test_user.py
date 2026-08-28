from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User


class Command(BaseCommand):
    help = "Create a local test user if testuser does not exist."

    def handle(self, *args, **options):
        now = timezone.now()
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                "student_no": "test001",
                "real_name": "测试用户",
                "phone": "13800000000",
                "department": "测试学院",
                "credit_score": 100,
                "role": "USER",
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            },
        )

        if not created:
            self.stdout.write(
                self.style.WARNING("testuser 已存在，跳过创建，未修改现有用户数据。")
            )
            return

        user.set_password("123456")
        user.save(update_fields=["password_hash"])
        self.stdout.write(
            self.style.SUCCESS("测试账号已创建：testuser / 123456")
        )
