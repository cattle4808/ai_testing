from rest_framework.urls import path

from api.bot import views


urlpatterns = [
    path('webhook/', views.TelegramWebhookView.as_view()),
]