from django.urls import path

from apps.agent import views


app_name = "agent"

urlpatterns = [
    path("", views.agent_chat_page, name="chat"),
    path("chat/", views.agent_chat_api, name="chat_api"),
]
