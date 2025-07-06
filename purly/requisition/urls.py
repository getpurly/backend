from django.urls import path
from rest_framework import routers

from .views import (
    RequisitionLineListView,
    RequisitionLineMineListView,
    RequisitionMineListView,
    RequisitionViewSet,
)

router = routers.SimpleRouter()

router.register(r"", RequisitionViewSet, basename="requisitions")

urlpatterns = [
    path("mine/", RequisitionMineListView.as_view()),
    path("lines/", RequisitionLineListView.as_view()),
    path("lines/mine/", RequisitionLineMineListView.as_view()),
]

urlpatterns += router.urls
