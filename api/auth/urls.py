from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from api.auth.bee import WorkerBeeView, EmployerBeeView
from api.auth.user import UserCreateView
from .user import UserView

urlpatterns = [
    path('token/', obtain_auth_token),
    path('user/', UserView.as_view()),
    path('new/', UserCreateView.as_view()),
    path('worker/', WorkerBeeView.as_view()),
    path('employer/', EmployerBeeView.as_view()),
]