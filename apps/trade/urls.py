from django.urls import path

from apps.trade import views


app_name = "trade"

urlpatterns = [
    path(
        "payment/success/<int:order_id>/",
        views.payment_success_view,
        name="payment_success",
    ),
    path("payment/<int:listing_id>/", views.payment_view, name="payment"),
    path("orders/<int:order_id>/", views.order_detail_view, name="order_detail"),
]
