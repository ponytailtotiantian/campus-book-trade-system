from django.urls import path

from apps.catalog import views


app_name = "catalog"

urlpatterns = [
    path("", views.listing_list, name="listing_list"),
    path("search/", views.listing_search, name="listing_search"),
    path("category/<int:category_id>/", views.listing_category, name="listing_category"),
    path("<int:listing_id>/", views.listing_detail, name="listing_detail"),
]
