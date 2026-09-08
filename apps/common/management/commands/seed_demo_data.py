from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Book, BookCategory, BookCondition
from apps.marketplace.models import Listing


class Command(BaseCommand):
    help = "Seed extra demo users and listings for local acceptance testing."

    def handle(self, *args, **options):
        now = timezone.now()
        seller = self._ensure_user(
            "demo_seller", "demo001", "演示卖家", "13990001001", "计算机学院"
        )
        self._ensure_user(
            "demo_student", "demo002", "演示学生", "13990001002", "软件学院"
        )

        categories = {
            item.category_name: item
            for item in BookCategory.objects.filter(status="ACTIVE")
        }
        conditions = {
            item.condition_name: item for item in BookCondition.objects.all()
        }

        demo_items = [
            ("数据库系统原理习题集", "9787300001011", "王珊", "数据库系统", "教材-计算机", "八成新", "SALE", "18.00", 3, "适合数据库课程复习，重点章节有少量标注。", ""),
            ("操作系统概念精要", "9787300001028", "汤小丹", "操作系统", "教材-计算机", "九成新", "SALE", "22.00", 2, "封面完整，内页干净，适合期末复习。", ""),
            ("计算机组成原理笔记版", "9787300001035", "白中英", "计算机组成原理", "教材-计算机", "有笔记", "SALE", "16.50", 2, "有课堂笔记和重点圈画，复习很方便。", ""),
            ("Java程序设计教程", "9787300001042", "张明", "Java程序设计", "编程", "九成新", "SALE", "26.00", 2, "配套实验课使用，代码示例完整。", ""),
            ("Python数据分析入门", "9787300001059", "李雷", "Python程序设计", "编程-Python", "八成新", "SALE", "24.00", 3, "适合Python入门和数据分析练习。", ""),
            ("Python爬虫实践手册", "9787300001066", "陈晨", "Python程序设计", "编程-Python", "九成新", "DONATION", "0.00", 2, "毕业整理书架，免费送给需要学习爬虫的同学。", "仅限校内自提，先到先得。"),
            ("高等数学同步练习册", "9787300001073", "同济大学数学系", "高等数学", "教材-数学", "七成新", "SALE", "12.00", 4, "部分题目有答案标注，适合刷题。", ""),
            ("线性代数辅导讲义", "9787300001080", "李永乐", "线性代数", "教材-数学", "八成新", "DONATION", "0.00", 3, "考完后闲置，免费捐给低年级同学。", "优先给大一新生或补考复习同学。"),
            ("考研英语真题解析", "9787300001097", "张剑", "考研英语", "考研-英语", "有笔记", "SALE", "28.00", 2, "近十年真题解析，有做题痕迹。", ""),
            ("考研政治核心考点", "9787300001103", "肖秀荣", "考研政治", "考研", "八成新", "SALE", "20.00", 2, "适合基础复习阶段使用。", ""),
            ("英语四级词汇速记", "9787300001110", "俞敏洪", "大学英语", "考研-英语", "六成新", "DONATION", "0.00", 2, "词汇书旧一些，但内容完整。", "自提即可，不收费用。"),
            ("人间词话注释版", "9787300001127", "王国维", "", "文学-散文", "九成新", "SALE", "15.00", 2, "文学选修课使用，保存很好。", ""),
            ("活着精装版", "9787300001134", "余华", "", "文学-小说", "八成新", "SALE", "18.00", 2, "课外阅读书，轻微翻阅痕迹。", ""),
            ("平凡的世界旧版", "9787300001141", "路遥", "", "文学-小说", "六成新", "DONATION", "0.00", 1, "宿舍搬迁，免费赠送。", "书较厚，建议到宿舍区自提。"),
            ("软件工程课程设计指导", "9787300001158", "课程组", "软件工程", "教材-计算机", "内页整洁", "SALE", "19.90", 2, "适合课程设计参考，附项目结构说明。", ""),
        ]

        created = 0
        for item in demo_items:
            if self._create_listing(item, seller, categories, conditions, now):
                created += 1

        self.stdout.write(self.style.SUCCESS(f"演示数据补充完成，新增商品 {created} 条。"))
        self.stdout.write("测试买家账号：demo_student / 123456")
        self.stdout.write("测试卖家账号：demo_seller / 123456")

    def _ensure_user(self, username, student_no, real_name, phone, department):
        user = (
            User.objects.filter(username=username).first()
            or User.objects.filter(student_no=student_no).first()
            or User.objects.filter(phone=phone).first()
        )
        now = timezone.now()
        if user is None:
            user = User(
                username=username,
                student_no=student_no,
                real_name=real_name,
                phone=phone,
                department=department,
                credit_score=100,
                role="USER",
                status="ACTIVE",
                created_at=now,
                updated_at=now,
            )
        else:
            user.username = username
            user.student_no = student_no
            user.real_name = real_name
            user.department = department
            user.status = "ACTIVE"
            user.updated_at = now
        user.set_password("123456")
        user.save()
        return user

    def _category(self, categories, name):
        return categories.get(name) or categories.get("教材") or next(iter(categories.values()))

    def _condition(self, conditions, name):
        return conditions.get(name) or conditions.get("八成新") or next(iter(conditions.values()))

    def _create_listing(self, item, seller, categories, conditions, now):
        (
            title,
            isbn,
            author,
            course_name,
            category_name,
            condition_name,
            listing_type,
            price,
            stock,
            description,
            donation_note,
        ) = item
        if Book.objects.filter(isbn=isbn).exists():
            return False

        book = Book.objects.create(
            category=self._category(categories, category_name),
            title=title,
            isbn=isbn,
            author=author,
            publisher="校园资料社",
            course_name=course_name or None,
            original_price=Decimal("59.80"),
            edition="演示版",
            publish_year=2024,
            created_at=now,
        )
        Listing.objects.create(
            seller=seller,
            book=book,
            condition=self._condition(conditions, condition_name),
            listing_type=listing_type,
            price=Decimal(price),
            stock=stock,
            description=description,
            donation_note=donation_note or None,
            status="ON_SALE",
            published_at=now,
            updated_at=now,
        )
        return True
