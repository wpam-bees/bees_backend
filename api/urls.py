from django.urls import include, path
from . import bees, auth


app_name = 'api'
urlpatterns = [
    path('auth/', include(auth.urls)),
    path('bees/', include(bees.urls)),
]
