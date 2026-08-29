"""Read-only Agent tools backed by Django ORM."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from django.db.models import Q
from django.utils import timezone

from apps.catalog.models import BookCategory
from apps.marketplace.models import Listing
from apps.trade.models import Order

from apps.agent.schemas import (
    ToolValidationError,
    authentication_required_result,
    clean_text,
    iso_or_none,
    normalize_limit,
    not_found_result,
    parse_non_negative_decimal,
    parse_positive_id,
    validate_listing_type,
    validate_order_status,
    validate_role,
    validation_error,
)


def _onsale_listing_qs():
    return Listing.objects.filter(status="ON_SALE").select_related(
        "book__category", "condition", "seller"
    )


def _category_ids_with_descendants(category: str | None) -> list[int] | None:
    category = clean_text(category, "category", 100)
    if not category:
        return None

    matched_ids = list(
        BookCategory.objects.filter(
            status="ACTIVE", category_name__icontains=category
        ).values_list("category_id", flat=True)
    )
    collected: list[int] = []

    def collect(category_id: int) -> None:
        if category_id in collected:
            return
        collected.append(category_id)
        child_ids = BookCategory.objects.filter(
            parent_id=category_id, status="ACTIVE"
        ).values_list("category_id", flat=True)
        for child_id in child_ids:
            collect(child_id)

    for category_id in matched_ids:
        collect(category_id)
    return collected


def _apply_common_filters(qs, keyword=None, category=None, max_price=None, listing_type=None):
    keyword = clean_text(keyword, "keyword", 100)
    category = clean_text(category, "category", 100)
    max_price_value = parse_non_negative_decimal(max_price, "max_price")
    listing_type_value = validate_listing_type(listing_type)

    if keyword:
        qs = qs.filter(
            Q(book__title__icontains=keyword)
            | Q(book__author__icontains=keyword)
            | Q(book__isbn__icontains=keyword)
            | Q(book__course_name__icontains=keyword)
        )

    if category:
        category_ids = _category_ids_with_descendants(category)
        if not category_ids:
            return qs.none()
        qs = qs.filter(book__category_id__in=category_ids)

    if max_price_value is not None:
        qs = qs.filter(price__lte=max_price_value)

    if listing_type_value:
        qs = qs.filter(listing_type=listing_type_value)
    return qs


def _serialize_listing(item) -> dict[str, Any]:
    book = item.book
    return {
        "listing_id": item.listing_id,
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn or "",
        "publisher": book.publisher,
        "course_name": book.course_name or "",
        "category": book.category.category_name,
        "condition": item.condition.condition_name,
        "listing_type": item.listing_type,
        "price": str(item.price),
        "stock": item.stock,
        "seller_name": item.seller.real_name,
        "description": item.description or "",
        "published_at": iso_or_none(item.published_at),
    }


def _serialize_detail(item) -> dict[str, Any]:
    book = item.book
    return {
        "listing_id": item.listing_id,
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn or "",
        "publisher": book.publisher,
        "course_name": book.course_name or "",
        "original_price": str(book.original_price),
        "edition": book.edition or "",
        "publish_year": book.publish_year,
        "category": book.category.category_name,
        "condition": item.condition.condition_name,
        "listing_type": item.listing_type,
        "price": str(item.price),
        "stock": item.stock,
        "description": item.description or "",
        "donation_note": item.donation_note or "",
        "seller_name": item.seller.real_name,
        "seller_department": item.seller.department,
        "status": item.status,
        "published_at": iso_or_none(item.published_at),
    }


def _book_score(item, keyword: str | None, category: str | None) -> int:
    if not keyword:
        return 0
    text = keyword.lower()
    title = item.book.title.lower()
    author = item.book.author.lower()
    course_name = (item.book.course_name or "").lower()
    category_name = item.book.category.category_name.lower()
    publisher = item.book.publisher.lower()

    score = 0
    if text in title:
        score += 5
    if text in author:
        score += 3
    if text in course_name:
        score += 3
    if text in category_name:
        score += 3
    if text in publisher:
        score += 1
    if category and category.lower() in category_name:
        score += 2
    return score


def _published_timestamp(item) -> float:
    value = item.published_at or datetime.min.replace(tzinfo=timezone.utc)
    return value.timestamp()


def search_books(keyword=None, category=None, max_price=None, listing_type=None, limit=10):
    try:
        max_limit = normalize_limit(limit, default=10, maximum=20)
        qs = _apply_common_filters(
            _onsale_listing_qs(),
            keyword=keyword,
            category=category,
            max_price=max_price,
            listing_type=listing_type,
        )
    except ToolValidationError as exc:
        return validation_error(str(exc))

    results = [
        _serialize_listing(item)
        for item in qs.order_by("-published_at")[:max_limit]
    ]
    return {"results": results}


def get_book_detail(listing_id):
    try:
        listing_id_value = parse_positive_id(listing_id)
    except ToolValidationError as exc:
        return validation_error(str(exc))

    item = _onsale_listing_qs().filter(listing_id=listing_id_value).first()
    if item is None:
        return not_found_result(listing_id_value)
    return _serialize_detail(item)


def recommend_books(
    keyword=None,
    category=None,
    max_price=None,
    listing_type=None,
    prefer_low_price=True,
    limit=5,
):
    try:
        max_limit = normalize_limit(limit, default=5, maximum=10)
        keyword_value = clean_text(keyword, "keyword", 100)
        category_value = clean_text(category, "category", 100)
        qs = _apply_common_filters(
            _onsale_listing_qs(),
            keyword=keyword,
            category=category,
            max_price=max_price,
            listing_type=listing_type,
        )
        if isinstance(prefer_low_price, str):
            prefer_low_price = prefer_low_price.strip().lower() in {"1", "true", "yes", "y"}
        else:
            prefer_low_price = bool(prefer_low_price)
    except ToolValidationError as exc:
        return validation_error(str(exc))

    candidates = list(qs)
    if prefer_low_price:
        candidates.sort(
            key=lambda item: (
                -_book_score(item, keyword_value, category_value),
                item.price,
                _published_timestamp(item),
            )
        )
    else:
        candidates.sort(
            key=lambda item: (
                -_book_score(item, keyword_value, category_value),
                -_published_timestamp(item),
                item.price,
            )
        )

    results = [_serialize_listing(item) for item in candidates[:max_limit]]
    return {"results": results}


def _serialize_order(order) -> dict[str, Any]:
    pickup = getattr(order, "pickup_record", None)
    return {
        "order_id": order.order_id,
        "book_title": order.listing.book.title,
        "listing_id": order.listing_id,
        "total_amount": str(order.total_amount),
        "order_type": order.order_type,
        "status": order.status,
        "created_at": iso_or_none(order.created_at),
        "paid_at": iso_or_none(order.paid_at),
        "completed_at": iso_or_none(order.completed_at),
        "cancelled_at": iso_or_none(order.cancelled_at),
        "buyer_name": order.buyer.real_name,
        "seller_name": order.seller.real_name,
        "pickup_code": pickup.pickup_code if pickup else None,
        "pickup_status": pickup.status if pickup else None,
        "pickup_point_name": pickup.pickup_point.name if pickup else None,
    }


def get_my_orders(
    request,
    order_id=None,
    status=None,
    order_type=None,
    role="buyer",
    limit=20,
):
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return authentication_required_result()
    user_id = getattr(user, "user_id", None)
    if user_id is None:
        return authentication_required_result()

    try:
        role_value = validate_role(role)
        status_value = validate_order_status(status)
        order_type_value = validate_listing_type(order_type)
        order_id_value = parse_positive_id(order_id) if order_id is not None else None
        max_limit = normalize_limit(limit, default=20, maximum=50)
    except ToolValidationError as exc:
        return validation_error(str(exc))

    qs = Order.objects.filter(Q(buyer_id=user_id) | Q(seller_id=user_id))
    if role_value == "buyer":
        qs = qs.filter(buyer_id=user_id)
    elif role_value == "seller":
        qs = qs.filter(seller_id=user_id)

    if order_id_value is not None:
        qs = qs.filter(order_id=order_id_value)
    if status_value:
        qs = qs.filter(status=status_value)
    if order_type_value:
        qs = qs.filter(order_type=order_type_value)

    qs = (
        qs.select_related("listing__book", "buyer", "seller", "pickup_record__pickup_point")
        .order_by("-created_at")[:max_limit]
    )
    return {"orders": [_serialize_order(order) for order in qs]}
