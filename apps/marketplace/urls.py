from django.urls import path

from apps.marketplace import views


app_name = "marketplace"

urlpatterns = [
    path("listings/new/", views.listing_create, name="listing_create"),
]
