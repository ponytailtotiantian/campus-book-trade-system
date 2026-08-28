from django.shortcuts import render

from apps.accounts.models import User
from apps.catalog.models import BookCategory
from apps.marketplace.models import Listing


def home(request):
    context = {
        "page_title": "校园二手书交易系统",
        "db_ok": False,
        "listing_count": 0,
        "onsale_count": 0,
        "user_count": 0,
        "categories": [],
        "listings": [],
    }
    try:
        context["categories"] = list(
            BookCategory.objects.filter(status="ACTIVE").order_by(
                "sort_order", "category_id"
            )
        )
        context["listings"] = list(
            Listing.objects.filter(status="ON_SALE")
            .select_related("book__category", "condition", "seller")
            .order_by("-published_at")[:8]
        )
        context["listing_count"] = Listing.objects.count()
        context["onsale_count"] = Listing.objects.filter(status="ON_SALE").count()
        context["user_count"] = User.objects.count()
        context["db_ok"] = True
    except Exception:
        context["categories"] = []
        context["listings"] = []
    return render(request, "home.html", context)
