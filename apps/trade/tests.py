from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from apps.trade.views import payment_view


class PaymentViewTests(SimpleTestCase):
    def test_donation_order_does_not_require_card_number(self):
        request = RequestFactory().post("/trade/payment/7/", data={})
        request.user = SimpleNamespace(is_authenticated=True, user_id=3)
        listing = SimpleNamespace(
            listing_id=7,
            listing_type="DONATION",
            seller_id=1,
            status="ON_SALE",
            stock=1,
        )

        with patch("apps.trade.views._get_purchase_listing", return_value=listing), patch(
            "apps.trade.views._create_mock_order", return_value=88
        ) as create_order:
            response = payment_view(request, listing.listing_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/trade/payment/success/88/")
        create_order.assert_called_once_with(
            listing,
            request.user.user_id,
            "捐赠书籍领取申请已确认",
        )
