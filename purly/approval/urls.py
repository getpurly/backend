from django.urls import path
from rest_framework import routers

from .views import ApprovalMineListView, ApprovalViewSet

router = routers.SimpleRouter()

router.register(r"", ApprovalViewSet, basename="approvals")

urlpatterns = [
    path("mine/", ApprovalMineListView.as_view()),
]

urlpatterns += router.urls
