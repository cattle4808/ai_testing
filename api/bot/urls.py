from rest_framework.urls import path

from api.bot import views


urlpatterns = [
    path('webhook/', views.webhook),

    path('create_script_select_time/', views.create_script_view),
    path('select_time/', views.select_time)
    # path('select_time/', )
]