from . import views
from django.urls import path

urlpatterns = [
    path("webhook/github/", views.github_webhook, name="github_webhook"),
    path("api/events", views.get_events, name="get_events"),
    path("", views.event_dashboard, name="event_dashboard"),
]
