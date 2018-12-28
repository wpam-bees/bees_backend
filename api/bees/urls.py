from django.urls import path
from rest_framework.routers import DefaultRouter

from api.bees.braintree import BraintreeViewSet
from api.bees.employer_bee import EmployerBeeViewSet

from api.bees.category import CategoryViewSet
from api.bees.filter import FiltersView
from api.bees.job import JobViewSet
from api.bees.worker_bee import WorkerBeeViewSet

router = DefaultRouter()

router.register('worker_bee', WorkerBeeViewSet)
router.register('employer_bee', EmployerBeeViewSet)
router.register('category', CategoryViewSet)
router.register('job', JobViewSet)
router.register('braintree', BraintreeViewSet, base_name='braintree')

app_name = 'bees_api'
urlpatterns = router.urls + [
    path('filters/', FiltersView.as_view()),
]
