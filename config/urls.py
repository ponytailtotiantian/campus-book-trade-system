from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.common import views as common_views


urlpatterns = [
    path("", common_views.home, name="home"),
    path("catalog/", include("apps.catalog.urls")),
    path("marketplace/", include("apps.marketplace.urls")),
    path("trade/", include("apps.trade.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("agent/", include("apps.agent.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
