from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, connection
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import urlencode

from apps.catalog.models import PickupPoint
from apps.marketplace.models import Listing
from apps.pickup.models import PickupRecord

from apps.trade.forms import MockPaymentForm
from apps.trade.models import Order


class PurchaseBlocked(Exception):
    pass


def _get_purchase_listing(listing_id):
    return get_object_or_404(
        Listing.objects.select_related("book", "condition", "seller"),
        listing_id=listing_id,
    )


def _validate_purchase_listing(listing, user):
    if listing.status != "ON_SALE":
        raise PurchaseBlocked("该商品当前不在售。")
    if listing.seller_id == user.user_id:
        raise PurchaseBlocked("不能购买自己发布的商品。")
    if listing.stock <= 0:
        raise PurchaseBlocked("该商品库存不足，暂时无法购买。")


def _blocked_redirect(listing_id, message):
    url = reverse("catalog:listing_detail", args=[listing_id])
    return redirect(f"{url}?{urlencode({'purchase_error': message})}")


def _active_pickup_points():
    return PickupPoint.objects.filter(status="ACTIVE").order_by("pickup_point_id")


def _default_pickup_point_id():
    pickup_point = _active_pickup_points().first()
    return pickup_point.pickup_point_id if pickup_point else None


def _resolve_pickup_point_id(value):
    if not value:
        pickup_point_id = _default_pickup_point_id()
        if pickup_point_id is None:
            raise PurchaseBlocked("当前没有可用的自提点，暂时无法创建订单。")
        return pickup_point_id

    try:
        pickup_point_id = int(value)
    except (TypeError, ValueError) as exc:
        raise PurchaseBlocked("请选择有效的自提点。") from exc

    if not PickupPoint.objects.filter(
        pickup_point_id=pickup_point_id, status="ACTIVE"
    ).exists():
        raise PurchaseBlocked("请选择有效的自提点。")
    return pickup_point_id


def _render_payment(request, listing, form, selected_pickup_point_id=None, payment_error=None):
    try:
        selected_pickup_point_id = (
            int(selected_pickup_point_id) if selected_pickup_point_id else None
        )
    except (TypeError, ValueError):
        selected_pickup_point_id = None
    selected_pickup_point_id = selected_pickup_point_id or _default_pickup_point_id()
    return render(
        request,
        "trade/payment.html",
        {
            "listing": listing,
            "form": form,
            "pickup_points": _active_pickup_points(),
            "selected_pickup_point_id": selected_pickup_point_id,
            "payment_error": payment_error,
        },
    )


def _create_mock_order(listing, buyer_id, pickup_point_id, remark):
    with connection.cursor() as cursor:
        cursor.callproc(
            "proc_create_order_with_pickup",
            [
                listing.listing_id,
                buyer_id,
                pickup_point_id,
                remark,
            ],
        )
        row = cursor.fetchone()
        if row is None or not row[0]:
            raise PurchaseBlocked("订单创建失败，请稍后重试。")
        return int(row[0])


@login_required
def payment_view(request, listing_id):
    listing = _get_purchase_listing(listing_id)
    try:
        _validate_purchase_listing(listing, request.user)
    except PurchaseBlocked as exc:
        return _blocked_redirect(listing_id, str(exc))

    if request.method == "POST":
        selected_pickup_point_id = request.POST.get("pickup_point_id")
        if listing.listing_type == "DONATION":
            try:
                pickup_point_id = _resolve_pickup_point_id(selected_pickup_point_id)
                order_id = _create_mock_order(
                    listing,
                    request.user.user_id,
                    pickup_point_id,
                    "捐赠书籍领取申请已确认",
                )
            except PurchaseBlocked as exc:
                return _render_payment(
                    request,
                    listing,
                    MockPaymentForm(),
                    selected_pickup_point_id,
                    str(exc),
                )
            except DatabaseError:
                return _render_payment(
                    request,
                    listing,
                    MockPaymentForm(),
                    selected_pickup_point_id,
                    "领取订单创建失败，请稍后重试。",
                )
            return redirect("trade:payment_success", order_id=order_id)

        form = MockPaymentForm(request.POST)
        if form.is_valid():
            try:
                pickup_point_id = _resolve_pickup_point_id(selected_pickup_point_id)
                order_id = _create_mock_order(
                    listing,
                    request.user.user_id,
                    pickup_point_id,
                    "模拟信用卡支付成功",
                )
            except PurchaseBlocked as exc:
                return _render_payment(
                    request,
                    listing,
                    form,
                    selected_pickup_point_id,
                    str(exc),
                )
            except DatabaseError:
                return _render_payment(
                    request,
                    listing,
                    form,
                    selected_pickup_point_id,
                    "订单创建失败，请稍后重试。",
                )
            else:
                return redirect("trade:payment_success", order_id=order_id)
        return _render_payment(request, listing, form, selected_pickup_point_id)

    return _render_payment(request, listing, MockPaymentForm())


@login_required
def payment_success_view(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("listing__book", "buyer", "seller"),
        order_id=order_id,
        buyer=request.user,
    )
    return render(
        request,
        "trade/payment_success.html",
        {"order": order},
    )


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("listing__book", "buyer", "seller"),
        order_id=order_id,
        buyer=request.user,
    )
    pickup = (
        PickupRecord.objects.select_related("pickup_point")
        .filter(order=order)
        .first()
    )
    return render(
        request,
        "trade/order_detail.html",
        {"order": order, "pickup": pickup},
    )
