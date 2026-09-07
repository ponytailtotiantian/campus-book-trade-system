from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from apps.catalog.models import BookCategory
from apps.marketplace.models import Listing


def _active_categories():
    return BookCategory.objects.filter(status="ACTIVE").order_by("sort_order", "category_id")


def _category_ids_with_descendants(category_id):
    ids = [category_id]
    children = BookCategory.objects.filter(
        parent_id=category_id, status="ACTIVE"
    ).only("category_id")
    for child in children:
        ids.extend(_category_ids_with_descendants(child.category_id))
    return ids


def _onsale_listings():
    return (
        Listing.objects.filter(status="ON_SALE", stock__gt=0)
        .select_related("book__category", "condition", "seller")
    )


def _apply_search(queryset, q):
    q = (q or "").strip()
    if not q:
        return queryset
    return queryset.filter(
        Q(book__title__icontains=q)
        | Q(book__author__icontains=q)
        | Q(book__isbn__icontains=q)
    )


def _apply_sort(queryset, sort):
    if sort == "price_asc":
        return queryset.order_by("price", "-published_at")
    if sort == "price_desc":
        return queryset.order_by("-price", "-published_at")
    if sort == "title":
        return queryset.order_by("book__title", "-published_at")
    return queryset.order_by("-published_at")


def _catalog_context(request, queryset, category=None, q=""):
    q = (q or "").strip()
    sort = request.GET.get("sort", "latest")
    selected_category_id = category.category_id if category else request.GET.get("category")
    if selected_category_id:
        try:
            selected_category_id = int(selected_category_id)
        except (TypeError, ValueError):
            selected_category_id = ""
    else:
        selected_category_id = ""

    queryset = _apply_search(queryset, q)
    if selected_category_id:
        category_ids = _category_ids_with_descendants(selected_category_id)
        queryset = queryset.filter(book__category_id__in=category_ids)

    queryset = _apply_sort(queryset, sort)
    page_obj = Paginator(queryset, 12).get_page(request.GET.get("page"))
    return {
        "page_obj": page_obj,
        "listings": page_obj.object_list,
        "categories": _active_categories(),
        "selected_category_id": selected_category_id,
        "current_category": category,
        "q": q,
        "sort": sort,
    }


def listing_list(request):
    context = _catalog_context(request, _onsale_listings())
    return render(request, "catalog/listing_list.html", context)


def listing_search(request):
    context = _catalog_context(
        request, _onsale_listings(), q=request.GET.get("q", "")
    )
    return render(request, "catalog/listing_list.html", context)


def listing_category(request, category_id):
    category = get_object_or_404(
        BookCategory, category_id=category_id, status="ACTIVE"
    )
    context = _catalog_context(request, _onsale_listings(), category=category)
    return render(request, "catalog/listing_list.html", context)


def listing_detail(request, listing_id):
    listing = get_object_or_404(
        Listing.objects.select_related("book__category", "condition", "seller"),
        listing_id=listing_id,
        status="ON_SALE",
        stock__gt=0,
    )
    return render(
        request,
        "catalog/listing_detail.html",
        {"listing": listing, "categories": _active_categories()},
    )
