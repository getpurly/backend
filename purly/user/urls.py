from django.urls import path
from rest_framework import routers

from .views import UserMeRetrieveAPIView, UserViewSet

router = routers.SimpleRouter()

router.register(r"", UserViewSet, basename="users")

urlpatterns = [path("me/", UserMeRetrieveAPIView.as_view())]

urlpatterns += router.urls
