from rest_framework.urls import path

from . import views

urlpatterns = [
    path('create_script/', views.CreateIdScriptApiView.as_view()),
    path('get_or_create_tg_user/', views.GetOrCreateTgUserView.as_view()),
    path('get_my_scripts/', views.GetMyScriptsView.as_view()),
    path('change_script_isactive/<str:key>', views.ChangeIsActivateView.as_view()),
    path('change_script_time/', views.ChangeScriptTimeView.as_view()),
]

