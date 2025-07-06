from django.urls import path
from rest_framework import routers

from .views import AddressMineListView, AddressViewSet

router = routers.SimpleRouter()

router.register(r"", AddressViewSet, basename="addresses")

urlpatterns = [
    path("mine/", AddressMineListView.as_view()),
]

urlpatterns += router.urls
