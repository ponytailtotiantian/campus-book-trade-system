from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.catalog.models import Book
from apps.marketplace.forms import ListingCreateForm
from apps.marketplace.models import Listing


@login_required
def listing_create(request):
    if request.method == "POST":
        form = ListingCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with transaction.atomic():
                book = Book(
                    category=data["category"],
                    title=data["title"],
                    isbn=data.get("isbn") or None,
                    author=data["author"],
                    publisher=data["publisher"],
                    course_name=data.get("course_name") or None,
                    original_price=data.get("original_price") or Decimal("0.00"),
                    edition=data.get("edition") or None,
                    publish_year=data.get("publish_year"),
                    created_at=timezone.now(),
                )
                book.save()
                listing = Listing(
                    seller=request.user,
                    book=book,
                    condition=data["condition"],
                    listing_type=data["listing_type"],
                    price=data["price"] or Decimal("0.00"),
                    stock=data["stock"],
                    description=data.get("description") or None,
                    donation_note=data.get("donation_note") or None,
                    status="ON_SALE",
                    published_at=timezone.now(),
                    updated_at=timezone.now(),
                )
                listing.save()
            return redirect("catalog:listing_detail", listing_id=listing.listing_id)
    else:
        form = ListingCreateForm()

    return render(request, "marketplace/listing_create.html", {"form": form})
